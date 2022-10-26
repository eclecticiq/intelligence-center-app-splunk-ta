"""Formatters.py ."""
import traceback
import requests

from constants.general import (
    GET,
    PROXY_PASSWORD,
    PROXY_PORT,
    PROXY_TYPE_HTTP,
    PROXY_TYPE_HTTPS,
    PROXY_URL,
    PROXY_USERNAME,
    STANZA,
    STR_COLON,
    STR_FIVE,
)
from constants.messages import API_ERROR, EVENTS_RESPONSE_ERROR_CODE


def format_proxy_uri(proxy_dict):
    """
    Get Function to get proxy uri in format of.

    <protocol>://<user_name>:<password>@<proxy_server_ip>:<proxy_port>

    :param proxy_dict: dict, Dictionary containing proxy information
    :return: proxy_uri: str, proxy uri in standard format
    """
    uname = requests.compat.quote_plus(proxy_dict.get(PROXY_USERNAME, ""))
    passwd = requests.compat.quote_plus(proxy_dict.get(PROXY_PASSWORD, ""))
    proxy_url = proxy_dict.get(PROXY_URL)
    proxy_port = proxy_dict.get(PROXY_PORT)
    if uname and passwd:
        proxy_uri = f"{PROXY_TYPE_HTTP}://{uname}:{passwd}@{proxy_url}:{proxy_port}"
    else:
        proxy_uri = f"{proxy_url}{STR_COLON}{proxy_port}"
    proxy_settings = {PROXY_TYPE_HTTPS: f"{proxy_uri}"}
    return proxy_settings


def send_request(helper, url, headers, params, proxy, configs):
    """Send an API request to the URL provided with headers and parameters.

    :param helper: Splunk helper to send request
    :type helper: BaseModInput
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
    input_name = configs[STANZA]
    helper.log_info(f"Request is made with verify ssl value = {configs['verify_ssl']}")

    if proxy:
        proxy_settings = format_proxy_uri(proxy)
    else:
        proxy_settings = None
    try:
        response = requests.request(
            GET,
            url,
            headers=headers,
            params=params,
            verify=configs["verify_ssl"],
            timeout=50,
            proxies=proxy_settings,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        if str(response.status_code).startswith(STR_FIVE):
            helper.log_critical(API_ERROR.format(input=input_name, err=err))
            helper.log_critical(
                EVENTS_RESPONSE_ERROR_CODE.format(
                    input=input_name,
                    code=response.status_code,
                    error=str(response.content),
                )
            )
        else:
            helper.log_error(API_ERROR.format(input=input_name, err=err))
            helper.log_error(
                EVENTS_RESPONSE_ERROR_CODE.format(
                    input=input_name,
                    code=response.status_code,
                    error=str(response.content),
                )
            )
        raise err
    except requests.exceptions.ConnectionError as err:
        helper.log_error(API_ERROR.format(input=input_name, err=err))
        raise err
    except requests.exceptions.Timeout as err:
        helper.log_error(API_ERROR.format(input=input_name, err=err))
        raise err
    except requests.exceptions.RequestException as err:
        helper.log_error(API_ERROR.format(input=input_name, err=err))
        helper.log_error(
            EVENTS_RESPONSE_ERROR_CODE.format(
                input=input_name,
                code=response.status_code,
                error=str(response.content),
            )
        )
        raise err
    except Exception as err:
        helper.log_error(traceback.format_exc())
        raise err
    return response
