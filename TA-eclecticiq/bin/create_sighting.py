# Copyright (c) 2017-2020 IronNet
# import ta_eclecticiq_declare
import os
import json
import sys
import requests

from splunk.persistconn.application import PersistentServerConnectionApplication
import logging, logging.handlers
import splunk


# Add the lib and current directory to the python path
(path, _) = os.path.split(os.path.realpath(__file__))
sys.path.insert(0, path)
sys.path.insert(0, os.path.join(path, "../lib"))
import os
import sys
from splunk.clilib import cli_common as cli
import datetime

SIGHTING_SCHEMA = {
    "data": {
        "data": {
            "confidence": "medium",
            "description": "test_desc",
            "type": "eclecticiq-sighting",
            "timestamp": "2022-03-10T05:37:42Z",
            "title": "title1",
            "security_control": {
                "type": "information-source",
                "identity": {
                    "name": "EclecticIQ Platform App for Qradar",
                    "type": "identity",
                },
                "time": {
                    "type": "time",
                    "start_time": "2022-03-10T05:37:42Z",
                    "start_time_precision": "second",
                },
            },
        },
        "meta": {"tags": ["Qradar Alert"], "ingest_time": "2022-03-10T05:37:42Z"},
    }
}

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

    def create_send_resp(self, response, status_code):
        logger.info(f"response={status_code}")
        return {
            "payload": response,
            "status": status_code,
            "headers": {"Content-Type": "application/json"},
        }

    def send_request(self, url, headers, sighting):
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
        logger.info("Send request called!")

        response = {}

        endpoint = url + "/entities"
        logger.info("Sending request!!")
        response = requests.request(
            "POST",
            url=endpoint,
            headers=headers,
            data=json.dumps(sighting),
            verify=False,
        )
        logger.info("After send request!")
        logger.info(response)
        logger.info(response.status_code)
        logger.info(endpoint)
        logger.info(response.content)
        return response

    def handle(self, in_string):

        logger.info("Request received.")
        in_dict = json.loads(in_string)
        appdir = os.path.dirname(os.path.dirname(__file__))
        localconfpath = os.path.join(appdir, "local", "ta_eclecticiq_account.conf")
        logger.info(localconfpath)
        apikeyconf = {}
        if os.path.exists(localconfpath):
            localconf = cli.readConfFile(localconfpath)
            logger.info(localconf)
            for name, content in localconf.items():
                if name != "default":
                    account_name = name
                    logger.info(account_name)
                if name in apikeyconf:
                    apikeyconf[name].update(content)
                else:
                    apikeyconf[name] = content
            logger.info(f"apikeyconf ={apikeyconf}")
            url = apikeyconf[account_name]["url"]
            logger.info(url)

        payload = self.parse_form_data(in_dict["form"])
        logger.info(payload)
        today = datetime.datetime.utcnow().date()
        sighting = SIGHTING_SCHEMA
        logger.info(sighting)
        time = datetime.datetime.utcnow()
        creds = json.loads(payload["creds"])
        logger.info(creds)
        api_key = json.loads(creds["eiq"])["api_key"]
        logger.info("api_key =" + api_key)
        sighting["data"]["data"]["value"] = payload["sighting_value"]
        sighting["data"]["data"]["description"] = payload["sighting_desc"]
        sighting["data"]["data"]["timestamp"] = datetime.datetime.strftime(
            time, "%Y-%m-%dT%H:%M:%S.%f"
        )
        sighting["data"]["data"]["confidence"] = payload["confidence_level"]
        sighting["data"]["data"]["title"] = payload["sighting_title"]
        sighting["data"]["meta"]["tags"] = [
            "".join(i for i in list(payload["sighting_tags"]))
        ]
        sighting["data"]["data"]["security_control"]["type"] = payload["sighting_type"]
        sighting["data"]["data"]["security_control"]["time"][
            "start_time"
        ] = datetime.datetime.strftime(
            datetime.datetime(today.year, today.month, today.day, 0, 0, 0),
            "%Y-%m-%dT%H:%M:%S.%f",
        )
        sighting["data"]["meta"]["ingest_time"] = datetime.datetime.strftime(
            time, "%Y-%m-%dT%H:%M:%S.%f"
        )
        logger.info(sighting)
        headers = {"Authorization": f"Bearer {api_key}"}
        response = self.send_request(url, headers, sighting)
        # return response
        logger.info(response.status_code)
        logger.info(response.content)
        # if (!(response.status_code).startsWith("2")) {
        #     logger.info("Request failed!Please try again!!")
        #     return
        # }
        # else {
        #     ret_value = {
        #         "response":response.status_code,
        #         "msg":"Sighting Created Successfully"
        #         }
        #     return ret_value
        #     try {
        #             logger.info(response)
        #             return
        #     } catch (e) {
        #             console.log(e)
        #             alert("Loading failed,Check Network connection!")
        #             return
