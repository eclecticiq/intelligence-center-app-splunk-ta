# Copyright (c) 2017-2020 IronNet

import datetime
from splunk.clilib import cli_common as cli

import os
import json
import sys
import requests
from splunk.persistconn.application import PersistentServerConnectionApplication
import logging
import logging.handlers
import splunk
import traceback



(path, _) = os.path.split(os.path.realpath(__file__))
sys.path.insert(0, path)
import ta_eclecticiq_declare
from constants.messages import API_ERROR, COULD_NOT_CREATE_SIGHTING, CREDS_NOT_FOUND, EVENTS_RESPONSE_ERROR_CODE, REQUEST_FAILED, SIGHTING_CREATED
from utils.formatters import format_proxy_uri
from constants.sighting_right_click import CONFIDENCE, CONFIDENCE_LEVEL, CONTENT_TYPE, DATA_STR, DESCRIPTION, INGEST_TIME, META, SECURITY_CONTROL, SIGHTING_DESC, SIGHTING_SCHEMA, SIGHTING_TAGS, SIGHTING_TITLE, SIGHTING_TYPE, SIGHTING_VALUE, START_TIME, TAGS, TIME,TIME_FORMAT, TEXT_PLAIN, TIMESTAMP_STR, TITLE, TYPE, VALUE, INPUT_NAME
from constants.general import AUTHORIZATION, CREDS, HEADERS, PAYLOAD, PROXY, PROXY_PASSWORD, STATUS_STR, URL
from constants.defaults import LOCAL_DIR, ACCOUNTS_CONF, SETTINGS_CONF


if sys.platform == "win32":
    import msvcrt

    # Binary mode is required for persistent mode on Windows.
    msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
    msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)
    msvcrt.setmode(sys.stderr.fileno(), os.O_BINARY)

# Setup logging
logger = logging.getLogger("splunk.ironnet_splunk")
SPLUNK_HOME = os.environ["SPLUNK_HOME"]

LOGGING_DEFAULT_CONFIG_FILE = os.path.join(SPLUNK_HOME, "etc", "log.cfg")
LOGGING_LOCAL_CONFIG_FILE = os.path.join(SPLUNK_HOME, "etc", "log-local.cfg")
LOGGING_STANZA_NAME = "python"
LOGGING_FILE_NAME = "ta_eclecticiq_create_sighting.log"
BASE_LOG_PATH = os.path.join("var", "log", "splunk")
LOGGING_FORMAT = "%(asctime)s %(levelname)-s\t%(module)s:%(lineno)d - %(message)s"
splunk_log_handler = logging.handlers.RotatingFileHandler(
    os.path.join(SPLUNK_HOME, BASE_LOG_PATH, LOGGING_FILE_NAME), mode="a"
)
splunk_log_handler.setFormatter(logging.Formatter(LOGGING_FORMAT))
logger.addHandler(splunk_log_handler)
splunk.setupSplunkLogger(
    logger, LOGGING_DEFAULT_CONFIG_FILE, LOGGING_LOCAL_CONFIG_FILE, LOGGING_STANZA_NAME
)


class Send(PersistentServerConnectionApplication):
    def __init__(self, command_line, command_arg):
        PersistentServerConnectionApplication.__init__(self)

    def parse_form_data(self, form_data):
        parsed = {}
        for [key, value] in form_data:
            parsed[key] = value
        return parsed

    def send_request(self, url, headers, proxy, sighting):
        """Send an API request to the URL provided with headers and parameters

        :param logger: Splunk logger to send request
        :type logger: BaseModInput
        :param url: API URL to send request
        :type url: str
        :param params: Parameters to be sent to API
        :type params: dict
        :param headers: Headers to be included in the request
        :type headers: dict
        :param proxy: proxy details to be included in the request
        :type proxy: dict
        :return: API response
        :rtype: dict
        """
        if proxy.get("proxy_enabled") == "1":
            proxy_settings = format_proxy_uri(proxy)
        else:
            proxy_settings = None
        try:
            response = requests.request(
                "post",
                url,
                headers=headers,
                data=json.dumps(sighting),
                verify=True,
                timeout=50,
                proxies=proxy_settings,
            )
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            if str(response.status_code).startswith("5"):
                logger.critical(API_ERROR.format(input=INPUT_NAME, err=err))
                logger.critical(
                    EVENTS_RESPONSE_ERROR_CODE.format(
                        input=INPUT_NAME,
                        code=response.status_code,
                        error=str(response.content),
                    )
                )
            else:
                logger.error(API_ERROR.format(input=INPUT_NAME, err=err))
                logger.error(
                    EVENTS_RESPONSE_ERROR_CODE.format(
                        input=INPUT_NAME,
                        code=response.status_code,
                        error=str(response.content),
                    )
                )
            raise err
        except requests.exceptions.ConnectionError as err:
            logger.error(API_ERROR.format(input=INPUT_NAME, err=err))
            raise err
        except requests.exceptions.Timeout as err:
            logger.error(API_ERROR.format(input=INPUT_NAME, err=err))
            raise err
        except requests.exceptions.RequestException as err:
            logger.error(API_ERROR.format(input=INPUT_NAME, err=err))
            logger.error(
                EVENTS_RESPONSE_ERROR_CODE.format(
                    input=INPUT_NAME,
                    code=response.status_code,
                    error=str(response.content),
                )
            )
            raise err
        except Exception as err:
            logger.error(traceback.format_exc())
            raise err
        return response

    def create_response(self, status, message):
        return {
            PAYLOAD: message,
            STATUS_STR: status,
            HEADERS:{
                CONTENT_TYPE: TEXT_PLAIN
            }
        }

    def get_url(self, path):
        apikeyconf = {}
        if os.path.exists(path):
            localconf = cli.readConfFile(path)
            for name, content in localconf.items():
                if name != "default":
                    account_name = name
                if name in apikeyconf:
                    apikeyconf[name].update(content)
                else:
                    apikeyconf[name] = content
            return apikeyconf[account_name][URL]

    def get_proxy(self, path):
        if os.path.exists(path):
            localsettingsconf = cli.readConfFile(path)
            for stanza, fields in localsettingsconf.items():
                if stanza == PROXY:
                    return fields

    def handle(self, in_string):
        """Handles request made to the endpoint services/create_sighting

        :param self: Object of the class
        :type in_string: Send
        :param in_string: Payload of the request in string
        :type in_string: str
        :return: Response to be send
        :rtype: dict
        """

        logger.info("Request received.")
        in_dict = json.loads(in_string)
        appdir = os.path.dirname(os.path.dirname(__file__))
        localconfpath = os.path.join(appdir, LOCAL_DIR, ACCOUNTS_CONF)
        url = self.get_url(localconfpath)
        localsettings_conf = os.path.join(appdir, LOCAL_DIR, SETTINGS_CONF)
        settingsconf = {}
        settingsconf[PROXY] = self.get_proxy(localsettings_conf)
        payload = self.parse_form_data(in_dict["form"])
        today = datetime.datetime.utcnow().date()
        sighting = SIGHTING_SCHEMA
        time = datetime.datetime.utcnow()
        api_key = payload.get(CREDS)
        if not api_key:
            return self.create_response(401, CREDS_NOT_FOUND)
        proxy_pass = payload.get("proxy_pass") if payload.get("proxy_pass") else ""
        if settingsconf[PROXY]:
            settingsconf[PROXY][PROXY_PASSWORD] = proxy_pass
        sighting[DATA_STR][DATA_STR][VALUE] = payload[SIGHTING_VALUE]
        sighting[DATA_STR][DATA_STR][DESCRIPTION] = payload[SIGHTING_DESC]
        sighting[DATA_STR][DATA_STR][TIMESTAMP_STR] = datetime.datetime.strftime(
            time, TIME_FORMAT
        )
        sighting[DATA_STR][DATA_STR][CONFIDENCE] = payload[CONFIDENCE_LEVEL]
        sighting[DATA_STR][DATA_STR][TITLE] = payload[SIGHTING_TITLE]
        sighting[DATA_STR][META][TAGS] = [
            "".join(i for i in list(payload[SIGHTING_TAGS]))
        ]
        sighting[DATA_STR][DATA_STR][SECURITY_CONTROL][TYPE] = payload[SIGHTING_TYPE]
        sighting[DATA_STR][DATA_STR][SECURITY_CONTROL][TIME][
            START_TIME
        ] = datetime.datetime.strftime(
            datetime.datetime(today.year, today.month, today.day, 0, 0, 0),
            TIME_FORMAT,
        )
        sighting[DATA_STR][META][INGEST_TIME] = datetime.datetime.strftime(
            time, TIME_FORMAT
        )
        headers = {AUTHORIZATION: f"Bearer {api_key}"}
        try:
            response = self.send_request(url + "/entities", headers, settingsconf[PROXY], sighting)
        except Exception as err:
            return self.create_response(500, err)
        if not (str(response.status_code)).startswith("2"):
            logger.info(REQUEST_FAILED)
            return self.create_response(response.status_code, COULD_NOT_CREATE_SIGHTING)
        else:
            content = json.loads(response.content)
            message = SIGHTING_CREATED.format(url, content[DATA_STR]["id"])
            logger.info(message)
            return self.create_response(response.status_code, message)
