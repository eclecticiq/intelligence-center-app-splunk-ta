"""Create Sighting Workflow Action."""
import datetime
import hashlib
import json
import logging
import os
import sys
import re
import traceback
import requests
from splunk.clilib import cli_common as cli
from splunk.persistconn.application import PersistentServerConnectionApplication


(path, _) = os.path.split(os.path.realpath(__file__))
sys.path.insert(0, path)
import ta_eclecticiq_declare  # noqa pylint: disable=C0413,W0611
import splunklib.client as client  # pylint: disable=C0413
from constants.defaults import (  # pylint: disable=C0413
    ACCOUNTS_CONF,
    LOCAL_DIR,
    SETTINGS_CONF,
)  # pylint: disable=C0413
from constants.general import (  # pylint: disable=C0413
    AUTHORIZATION,
    CREDS,
    HEADERS,
    PAYLOAD,
    PROXY,
    PROXY_PASSWORD,
    STATUS_STR,
    URL,
)  # pylint: disable=C0413
from constants.messages import (
    API_ERROR,
    COULD_NOT_CREATE_SIGHTING,
    CREDS_NOT_FOUND,
    EVENTS_RESPONSE_ERROR_CODE,
    JSON_EXCEPTION,
    REQUEST_FAILED,
    SIGHTING_CREATED,
)  # pylint: disable=C0413
from constants.sighting_right_click import (
    CONFIDENCE,
    CONFIDENCE_LEVEL,
    CONTENT_TYPE,
    DATA_STR,
    DESCRIPTION,
    INGEST_TIME,
    INPUT_NAME,
    META,
    SECURITY_CONTROL,
    SIGHTING_DESC,
    SIGHTING_SCHEMA,
    SIGHTING_TAGS,
    SIGHTING_TITLE,
    SIGHTING_TYPE,
    SIGHTING_VALUE,
    START_TIME,
    TAGS,
    TEXT_PLAIN,
    TIME,
    TIME_FORMAT,
    TIMESTAMP_STR,
    TITLE,
    TYPE,
    VALUE,
)  # pylint: disable=C0413
from utils.formatters import format_proxy_uri  # pylint: disable=C0413

from validator.logger_manager import setup_logging  # pylint: disable=C0413

if sys.platform == "win32":
    import msvcrt

    # Binary mode is required for persistent mode on Windows.
    msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)  # pylint: disable=E1101
    msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)  # pylint: disable=E1101
    msvcrt.setmode(sys.stderr.fileno(), os.O_BINARY)  # pylint: disable=E1101

# Setup logging
logger = setup_logging("ta_eclecticiq_create_sighting", log_level=logging.DEBUG)


class Send(PersistentServerConnectionApplication):  # type: ignore
    """Sends the sighting to EclecticIQ Platform."""

    def __init__(self, command_line, command_arg):  # pylint: disable=W0613
        PersistentServerConnectionApplication.__init__(self)

    @staticmethod
    def parse_form_data(form_data):
        """Parse the payload.

        :param form_data: payload of the request
        :type form_data: dict
        """
        parsed = {}
        for [key, value] in form_data:
            parsed[key] = value
        return parsed

    @staticmethod
    def send_request(method, url, verify_ssl, headers, proxy, data, params=None):
        """Send an API request to the URL provided with headers and parameters.

        :param url: API URL to send request
        :type url: str
        :param headers: Headers to be included in the request
        :type headers: dict
        :param proxy: proxy details to be included in the request
        :type proxy: dict
        :param sighting: payload of sighting
        :type sighting: dict
        :return: API response
        :rtype: dict
        """
        if proxy.get("proxy_enabled") == "1":
            proxy_settings = format_proxy_uri(proxy)
        else:
            proxy_settings = None
        try:
            if method == "get":
                response = requests.request(
                    method,
                    url,
                    headers=headers,
                    params=params,
                    verify=verify_ssl,
                    timeout=50,
                    proxies=proxy_settings,
                )
            else:
                response = requests.request(
                    method,
                    url,
                    headers=headers,
                    data=json.dumps(data),
                    verify=verify_ssl,
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

    @staticmethod
    def create_response(status, message):
        """Create response to send back to JS.

        :param status: status code
        :type status: int
        :param message: message to send
        :type message: str
        :return: response dict
        :rtype: dict
        """
        return {
            PAYLOAD: message,
            STATUS_STR: status,
            HEADERS: {CONTENT_TYPE: TEXT_PLAIN},
        }

    @staticmethod
    def get_url(api_conf_path):
        """Get the URL from accounts.conf.

        :param api_conf_path: path to the conf file
        :type api_conf_path: str
        :return: URL value from the conf
        :rtype: str
        """
        apikeyconf = {}
        if os.path.exists(api_conf_path):
            localconf = cli.readConfFile(api_conf_path)
            for name, content in localconf.items():
                if name != "default":
                    account_name = name
                if name in apikeyconf:
                    apikeyconf[name].update(content)
                else:
                    apikeyconf[name] = content
            return apikeyconf[account_name][URL]

    @staticmethod
    def get_verify_ssl(api_conf_path):
        """Get the URL from accounts.conf.

        :param api_conf_path: path to the conf file
        :type api_conf_path: str
        :return: URL value from the conf
        :rtype: str
        """
        apikeyconf = {}
        if os.path.exists(api_conf_path):
            localconf = cli.readConfFile(api_conf_path)
            for name, content in localconf.items():
                if name != "default":
                    account_name = name
                if name in apikeyconf:
                    apikeyconf[name].update(content)
                else:
                    apikeyconf[name] = content
            return apikeyconf.get(account_name).get("certificate_validation")

    @staticmethod
    def get_proxy(settings_conf_path):
        """Get the proxy from settings.conf.

        :param settings_conf_path: path to the conf file
        :type settings_conf_path: str
        :return: proxy information from the conf
        :rtype: dict
        """
        if os.path.exists(settings_conf_path):
            localsettingsconf = cli.readConfFile(settings_conf_path)
            for stanza, fields in localsettingsconf.items():
                if stanza == PROXY:
                    return fields
        return {}

    @staticmethod
    def get_response_content(response):
        """Get the response content from the response.

        :param response: Response to retrieve content
        :type response: Response
        :return: Response content
        :rtype: dict / None
        """
        content = {}
        try:
            content = json.loads(response.content)
        except json.decoder.JSONDecodeError as error:
            logger.error(JSON_EXCEPTION.format(error))

        return content

    @staticmethod
    def format_data(sighting, meta):
        """Fomat the data to store in KV store.

        :param sighting: Sighting related data
        :type sighting: dict
        :param meta: meta data from events
        :type meta: dict
        :return: formated dictionary to store
        :rtype: dict
        """
        data = {}
        data["alert_field"] = meta["field"]
        data["alert_source"] = "splunk_workflow"
        data["src"] = meta["src"]
        data["dest"] = meta["dest"]
        data["event_hash"] = meta["event_hash"]
        data["event_index"] = meta["index"]
        data["observable_id"] = meta["observable_id"]
        data["event_host"] = meta["host"]
        data["event_sourcetype"] = meta["sourcetype"]
        data["event_time"] = meta["time"]
        data["event_time_1"] = ""
        data["feed_id_eiq"] = meta["feed_id_eiq"]
        data["entity_title_eiq"] = sighting[DATA_STR][DATA_STR][TITLE]
        data["meta_entity_url_eiq"] = meta["meta_entity_url_eiq"]
        data["meta_tags_eiq"] = sighting[DATA_STR][META][TAGS]
        data["sighting"] = "1"
        data["source_name_eiq"] = ""
        data["timestamp_eiq"] = sighting[DATA_STR][DATA_STR][TIMESTAMP_STR]
        data["type_eiq"] = sighting[DATA_STR][DATA_STR][SECURITY_CONTROL][TYPE]
        data["value_eiq"] = sighting[DATA_STR][DATA_STR][VALUE]
        data["value_url_eiq"] = ""
        data["confidence_eiq"] = sighting[DATA_STR][DATA_STR]["confidence"]

        return data

    @staticmethod
    def store_sighting(data, session_key):
        """Store sighting in Splunk KV store.

        :param data: data to store
        :type data: dict
        :param session_key: session key for authentication
        :type session_key: str
        :return: stored or not stored
        :rtype: Bool,str
        """
        logger.info("In store sighting")
        insertion = False
        logger.info(data)
        service = client.connect(token=session_key, owner="nobody", app="TA-eclecticiq")

        collection = service.kvstore["eiq_alerts_list"]
        try:
            response = collection.data.insert(json.dumps(data))
            logger.info(response)
            insertion = response.get("_key")
        except requests.HTTPError as error:
            logger.info(error)
        except Exception as err:
            logger.info(err)
        return insertion

    @staticmethod
    def validate_type(s_type, value):  # pylint: disable=R0911
        """Get the type of the observable.

        :param value: observable value
        :type value: str
        :return: type of the observable
        :rtype: str
        """
        if s_type == "ipv4":  # pylint: disable=R1705
            return bool(re.match(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", value))
        elif s_type == "ipv6":
            return bool(
                re.match(
                    r"^(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))$",  # pylint: disable=C0301
                    value,
                )
            )
        elif s_type == "email":
            return bool(re.match(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]+", value))
        elif s_type == "uri":
            return bool(re.match(r"[^\:]+\:\/\/[\S]+", value))
        elif s_type == "domain":
            return bool(
                re.match(
                    r"^[a-zA-Z0-9][a-zA-Z0-9-]{1,61}[a-zA-Z0-9](?:\.[a-zA-Z]{2,})+$",
                    value,
                )
            )
        elif s_type == "hash-md5":
            return bool(re.match(r"^[a-f0-9A-F]{32}$", value))
        elif s_type == "hash-sha256":
            return bool(re.match(r"^[a-f0-9A-F]{64}$", value))
        elif s_type == "hash-sha1":
            return bool(re.match(r"\b[0-9a-f]{5,40}\b", value))
        elif s_type == "hash-sha512":
            return bool(re.match(r"^\w{128}$", value))
        elif s_type == "port":
            return bool(
                re.match(
                    r"^([1-9][0-9]{0,3}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])$",
                    value,
                )
            )
        else:
            return False

    def handle(self, in_string):  # pylint: disable=R0915,R0201
        """Handle request made to the endpoint services/create_sighting.

        :param self: Object of the class
        :type in_string: Send
        :param in_string: Payload of the request in string
        :type in_string: str
        :return: Response to be send
        :rtype: dict
        """
        logger.info("Request received.")
        in_dict = json.loads(in_string)
        session_dict = in_dict.get("session")
        session_key = session_dict.get("authtoken")
        appdir = os.path.dirname(os.path.dirname(__file__))
        localconfpath = os.path.join(appdir, LOCAL_DIR, ACCOUNTS_CONF)
        url = Send.get_url(localconfpath)

        verify_ssl = Send.get_verify_ssl(localconfpath)
        if verify_ssl == "1":  # pylint: disable=R1703
            verify_ssl = True
        else:
            verify_ssl = False

        logger.info(verify_ssl)

        localsettings_conf = os.path.join(appdir, LOCAL_DIR, SETTINGS_CONF)
        settingsconf = {}
        settingsconf[PROXY] = Send.get_proxy(localsettings_conf)
        payload = Send.parse_form_data(in_dict["form"])
        today = datetime.datetime.utcnow().date()
        sighting = SIGHTING_SCHEMA
        time = datetime.datetime.utcnow()
        api_key = payload.get(CREDS)

        if not api_key:
            return Send.create_response(401, CREDS_NOT_FOUND)
        proxy_pass = payload.get("proxy_pass") if payload.get("proxy_pass") else ""
        if settingsconf[PROXY]:
            settingsconf[PROXY][PROXY_PASSWORD] = proxy_pass
        meta_data = {}
        meta_data["host"] = payload["host"]
        meta_data["index"] = payload["index"]
        meta_data["observable_id"] = (
            payload.get("observable_id") if payload.get("observable_id") else ""
        )
        meta_data["source"] = payload["source"]
        meta_data["sourcetype"] = payload["sourcetype"]
        meta_data["time"] = payload["time"]
        meta_data["field"] = payload["field"]
        meta_data["src"] = payload["src"]
        meta_data["dest"] = payload["dest"]
        meta_data["event_hash"] = (
            hashlib.sha512(str(payload["_raw"]).encode("utf-8")).hexdigest()
            if payload.get("_raw")
            else payload.get("event_hash")
        )

        meta_data["feed_id_eiq"] = payload["feed_id_eiq"]
        meta_data["meta_entity_url_eiq"] = payload["meta_entity_url_eiq"]

        sighting[DATA_STR][DATA_STR][VALUE] = payload[SIGHTING_VALUE]
        if not Send.validate_type(payload[SIGHTING_TYPE], payload[SIGHTING_VALUE]):
            return Send.create_response(
                501, "Sighting value does not match with selected sighting type."
            )
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
            response = Send.send_request(
                "post",
                url + "/entities",
                verify_ssl,
                headers,
                settingsconf[PROXY],
                sighting,
            )
        except Exception as err:
            logger.error(err)
            return Send.create_response(500, str(err))
        if not (str(response.status_code)).startswith("2"):
            logger.info(REQUEST_FAILED)
            return Send.create_response(response.status_code, COULD_NOT_CREATE_SIGHTING)
        content = json.loads(response.content)
        hostname = url.split("/")
        hostname = "/".join(hostname[:-2])
        message = SIGHTING_CREATED.format(hostname, content[DATA_STR]["id"])
        logger.info(message)
        try:
            storage_data = Send.format_data(sighting, meta_data)
            is_stored = Send.store_sighting(storage_data, session_key)
            if not is_stored:
                logger.info(
                    "Sighting is not stored. link:{}/entity/{}.".format(
                        hostname, content[DATA_STR]["id"]
                    )
                )
            else:
                logger.info("Sighting is stored. Key:{}.".format(is_stored))
        except Exception:
            logger.info(traceback.format_exc())
        return Send.create_response(response.status_code, message)
