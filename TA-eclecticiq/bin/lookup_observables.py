import os
import json
import sys
import requests

from splunk.persistconn.application import PersistentServerConnectionApplication
import logging, logging.handlers
import splunk
from splunk.clilib import cli_common as cli
import traceback

# cfg = cli.getConfStanza("inputs", "eiq_observables://Puja")

logger = logging.getLogger("splunk.ironnet_splunk")
SPLUNK_HOME = os.environ["SPLUNK_HOME"]
LOGGING_DEFAULT_CONFIG_FILE = os.path.join(SPLUNK_HOME, "etc", "log.cfg")
LOGGING_LOCAL_CONFIG_FILE = os.path.join(SPLUNK_HOME, "etc", "log-local.cfg")
LOGGING_STANZA_NAME = "python"
LOGGING_FILE_NAME = "lookup_observables.log"
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

# logger.info(cfg)


# Add the lib and current directory to the python path
(path, _) = os.path.split(os.path.realpath(__file__))
logger.info(path)
sys.path.insert(0, path)
sys.path.insert(0, os.path.join(path, "../lib"))
import ta_eclecticiq_declare
import os
import sys
import datetime

logger.info(ta_eclecticiq_declare.ta_name)
logger.info(ta_eclecticiq_declare)
if sys.platform == "win32":
    import msvcrt

    # Binary mode is required for persistent mode on Windows.
    msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
    msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)
    msvcrt.setmode(sys.stderr.fileno(), os.O_BINARY)


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

    def prepare_observable_data(self, data):
        """Prepare Observable data to show on UI.

        :param data: Observable data
        :type data: dict
        :return: Only selected fields dict
        :rtype: dict
        """
        new_data = {}
        new_data["type"] = data.get("type")
        new_data["value"] = data.get("value")
        new_data["classification"] = data.get("meta").get("maliciousness")
        return new_data

    def prepare_entity_data(self, data, obs_data):
        """Prepare entity data to show on UI.

        :param data: Entity data
        :type data: dict
        :param data: Observable data
        :type data: list
        :return: Only selected fields dict
        :rtype: dict
        """
        new_data = {}
        if data.get("data"):
            new_data["title"] = (
                data.get("data").get("title") if data.get("data").get("title") else ""
            )

            new_data["description"] = (
                data.get("data").get("description")
                if data.get("data").get("description")
                else ""
            )
            new_data["confidence"] = (
                data.get("data").get("confidence")
                if data.get("data").get("confidence")
                else ""
            )
            new_data["tags"] = (
                data.get("data").get("tags") if data.get("data").get("tags") else ""
            )
        if data.get("meta"):
            new_data["threat_start_time"] = (
                data.get("meta").get("estimated_threat_start_time")
                if data.get("meta").get("estimated_threat_start_time")
                else ""
            )
            if data.get("data").get("producer"):
                new_data["source_name"] = (
                    data.get("data").get("producer").get("identity")
                    if data.get("data").get("producer").get("identity")
                    else ""
                )
            else:
                new_data["source_name"] = ""
            new_data["observables"] = obs_data

        return new_data

    def fetch_entity_details(self, entity_id):
        """Get entity details by id.

        :param entity_id: Entity ID
        :type: str
        :return: response content
        :rtype: dict
        """
        logger.info("In get fetch entity details..")
        logger.info(entity_id)
        url = "https://ic-playground.eclecticiq.com/api/beta"
        endpoint = url + "/entities" + "/" + entity_id

        api_key = "bcfa92a2d08afc8126a40e9b649808af6cce3440b59ade993e1e6d97856f0a85"
        headers = {"Authorization": f"Bearer {api_key}"}

        logger.info(endpoint)
        response = requests.request(
            "GET", endpoint, headers=headers, verify=False, timeout=50
        )

        logger.info(response.status_code)
        if response.status_code not in [200, 201]:
            return {}

        content = json.loads(response.content)
        data = content.get("data")
        logger.info(data)
        return data

    def get_observable_by_id(self, obs_id):
        """Get observables by id.

        :param obs_id: Observable ID
        :type: str
        :return: response content
        :rtype: dict
        """
        logger.info("In get observable by id .")
        api_key = "bcfa92a2d08afc8126a40e9b649808af6cce3440b59ade993e1e6d97856f0a85"
        headers = {"Authorization": f"Bearer {api_key}"}
        url = "https://ic-playground.eclecticiq.com/api/beta"
        endpoint = url + "/observables" + "/" + obs_id

        response = requests.request(
            "GET", endpoint, headers=headers, verify=False, timeout=50
        )

        logger.info(response.status_code)
        logger.info(response.content)
        if response.status_code not in [200, 201]:
            return {}

        content = json.loads(response.content)
        data = content.get("data")
        return data

    def get_entity_data(self, data_item):
        """Get entity data to show on UI.

        :param data_item: Data from lookup obsrvables Dict
        :type data_item: dict
        :param eiq_api: EIQ API object
        :type eiq_api: object
        :return: prepared data to show on UI
        :rtype: dict
        """
        logger.info("Inside Get entity data.")
        entity_data_dict = {}
        for item in data_item.get("entities"):
            entity_data = self.fetch_entity_details(str(item.split("/")[-1]))
            observables = (
                entity_data.get("observables") if entity_data.get("observables") else []
            )
            logger.info(observables)

            obs_data_list = []
            for observable in observables:
                obs_data = self.get_observable_by_id(str(observable.split("/")[-1]))

                append_data = self.prepare_observable_data(obs_data)

                obs_data_list.append(append_data)

            entity_data_dict.update(
                self.prepare_entity_data(entity_data, obs_data_list)
            )

        logger.info(entity_data_dict)
        return entity_data_dict

    def send_request(self, url, headers):
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
        obs_type = "uri"

        value = "http://178.175.122.131:51905/Mozi.a"
        parameters = {"filter[type]": obs_type, "filter[value]": value}
        endpoint = url + "/observables"
        logger.info("Sending request!!")
        response = requests.request(
            "GET",
            endpoint,
            headers=headers,
            params=parameters,
            verify=False,
            timeout=50,
        )

        logger.info("After send request!")

        logger.info(response.status_code)

        return response

    def handle(self, in_string):
        logger.info("Request received for lookup observables.")

        # logger.info(in_string)
        in_dict = json.loads(in_string)
        logger.info(in_dict)
        appdir = os.path.dirname(os.path.dirname(__file__))
        apikeyconfpath = os.path.join(appdir, "default", "ta_eclecticiq_account.conf")
        apikeyconf = cli.readConfFile(apikeyconfpath)
        localconfpath = os.path.join(appdir, "local", "ta_eclecticiq_account.conf")
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
        logger.info(apikeyconf["Puja"])
        api_key = logger.info(apikeyconf["Puja"]["api_key"])  # how to take the api key
        url = apikeyconf["Puja"]["url"]
        logger.info(apikeyconf["Puja"]["url"])

        payload = self.parse_form_data(in_dict["form"])
        # logger.info(payload)
        api_key = payload["api_key"]
        sighting_value = payload["sighting_value"]
        logger.info(api_key)
        logger.info(sighting_value)

        api_key = "bcfa92a2d08afc8126a40e9b649808af6cce3440b59ade993e1e6d97856f0a85"
        headers = {"Authorization": f"Bearer {api_key}"}
        response = self.send_request(url, headers)
        logger.info(response)
        final_data = []
        if str(response.status_code).startswith("2"):
            logger.info("Inside loop")
            data = json.loads(response.content)
            data = data["data"]

            for data_item in data:

                if data_item.get("entities"):
                    logger.info(data_item)
                    entity_data = self.get_entity_data(data_item)
                    final_data.append(entity_data)

        logger.info(final_data)

        return self.create_send_resp(final_data, response.status_code)
