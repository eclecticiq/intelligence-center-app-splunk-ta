# encoding = utf-8
# Always put this line at the beginning of this file
"""Create sighting alert action."""

import os
import sys
import json
import logging
import requests
import traceback
import hashlib

(path, _) = os.path.split(os.path.realpath(__file__))
sys.path.insert(0, path)
import ta_eclecticiq_declare  # noqa pylint: disable=C0413,W0611
from utils.formatters import format_proxy_uri  # pylint: disable=C0413
from constants.messages import (  # pylint: disable=C0413
    API_ERROR,  # pylint: disable=C0413
    EVENTS_RESPONSE_ERROR_CODE,  # pylint: disable=C0413
)  # pylint: disable=C0413

from validator.logger_manager import setup_logging  # pylint: disable=C0413
import splunklib.client as client  # pylint: disable=C0413

logger = setup_logging("ta_eclecticiq_create_sighting", log_level=logging.DEBUG)
INPUT_NAME = "create_sighting_alert_action"
current_dir = os.path.dirname(os.path.abspath(__file__))
SUPPORTED_TYPES = [
    "ipv4",
    "ipv6",
    "domain",
    "host",
    "uri",
    "hash-md5",
    "hash-sha1",
    "hash-sha256",
    "hash-sha512",
    "email",
    "port",
]


def send_request(method, url, headers, proxy, data, params=None):
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
                verify=True,
                timeout=50,
                proxies=proxy_settings,
            )
        else:
            response = requests.request(
                method,
                url,
                headers=headers,
                data=json.dumps(data),
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


def format_data(configuration, result):
    """Format the data.

    :param configuragtion: configurations from alert action
    :type configuragtion: dict
    :param result: results of search from alert
    :type result: dict
    :return: Formated payload
    :rtype: dict
    """
    record = {}
    record["sighting_value"] = (
        result.get(configuration.get("observable_value"))
        if configuration.get("observable_value")
        else ""
    )
    record["sighting_desc"] = (
        configuration.get("sighting_description")
        if configuration.get("sighting_description")
        else ""
    )
    record["sighting_title"] = (
        configuration.get("sighting_title")
        if configuration.get("sighting_title")
        else ""
    )
    record["sighting_tags"] = (
        configuration.get("sighting_tags") if configuration.get("sighting_tags") else ""
    )
    record["confidence_level"] = (
        configuration.get("sighting_confidence")
        if configuration.get("sighting_confidence")
        else ""
    )
    record["sighting_type"] = (
        configuration.get("observable_type")
        if configuration.get("observable_type")
        else ""
    )
    record["index"] = result.get("index") if result.get("index") else ""
    record["observable_id"] = (
        result.get("observable_id") if result.get("observable_id") else ""
    )
    record["host"] = result.get("host") if result.get("host") else ""
    record["source"] = result.get("source") if result.get("source") else ""
    record["sourcetype"] = result.get("sourcetype") if result.get("sourcetype") else ""
    record["time"] = result.get("_time") if result.get("_time") else ""
    record["field"] = (
        configuration.get("observable_value")
        if configuration.get("observable_value")
        else ""
    )
    record["src"] = result.get("src") if result.get("src") else ""
    record["dest"] = result.get("dest") if result.get("dest") else ""
    record["event_hash"] = (
        hashlib.sha512(result["_raw"])
        if result.get("_raw")
        else result.get("event_hash")
    )
    record["feed_id_eiq"] = (
        result.get("feed_id_eiq") if result.get("feed_id_eiq") else ""
    )
    record["meta_entity_url_eiq"] = (
        result.get("meta_entity_url_eiq") if result.get("meta_entity_url_eiq") else ""
    )
    return record


def main(payload):
    """Driver function."""
    session_key = str(payload["session_key"])
    # Get config params
    service = client.connect(token=session_key, owner="nobody", app="TA-eclecticiq")
    confs = service.confs
    url_val = ""
    account_name = ""
    for conf in confs:
        if conf.name == "ta_eclecticiq_account":
            stanzas = conf.list()
            for stanza in stanzas:
                url_val = stanza.content.get("url")
                account_name = stanza.name
                break
    sp_list = service.storage_passwords
    api_key = ""  # nosec
    proxy_pass = ""  # nosec
    for item in sp_list.list():
        if account_name in item.content.get(
            "username"
        ) and "splunk_cred_sep" not in item.content.get("clear_password"):
            creds = json.loads(item.content.get("clear_password"))
            api_key = creds["api_key"]
        if "proxy" in item.content.get(
            "username"
        ) and "splunk_cred_sep" not in item.content.get("clear_password"):
            creds = json.loads(item.content.get("clear_password"))
            proxy_pass = creds["proxy_password"]

    # make sure we have a username and a password
    # before we try to authenticate
    if not url_val:
        logger.error("No url provided via the config.")
        sys.exit(2)

    if not api_key:
        logger.error("No api_key found for user {}.".format(account_name))
        sys.exit(2)

    configuration = payload.get("configuration")
    result = payload.get("result")
    body_to_send = format_data(configuration, result)
    body_to_send["creds"] = api_key
    body_to_send["proxy_pass"] = proxy_pass
    if configuration.get("observable_type") not in SUPPORTED_TYPES:
        logger.error("Observable type is not in supported types")

    try:
        service.post("/services/create_sighting", body=body_to_send)
    except Exception:
        logger.error(traceback.format_exc())


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--execute":
        logger.info("Create sighting called from alert action.")
        arguments = json.loads(sys.stdin.read())
        main(arguments)
    else:
        print(
            "FATAL Unsupported execution mode (expected --execute flag)",
            file=sys.stderr,
        )
        sys.exit(2)
