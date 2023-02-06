# encoding = utf-8
"""Input module for entity and observable collection."""
from constants.defaults import (
    ADDITIONAL_PARAM_NUMBER_OF_RETRIES,
    ADDITIONAL_PARAM_PAGE_SIZE,
    ADDITIONAL_PARAM_SLEEP_TIME,
    ADDITIONAL_PARAMTERS_CONFIG,
    ADDITIONAL_PARAMTERS_STANZA,
    DEFAULT_NUMBER_OF_RETRIES,
    DEFAULT_PAGE_SIZE,
    DEFAULT_SLEEP_TIME,
)
from splunk.clilib import cli_common as cli
from constants.general import (
    API_KEY,
    DOMAIN,
    EMAIL,
    FILEHASH,
    GLOBAL_ACCOUNT,
    HOST_NAME,
    IP,
    OBSERVABLE_INGEST_TYPES,
    OUTGOING_FEEDS,
    PORT,
    STANZA,
    START_DATE,
    URI,
    URL,
    VERIFY_SSL,
)
from constants.messages import CURRENT_INPUT_STANZA, OUTGOING_FEED_IDS_SELECTED


def validate_input(helper, definition):  # pylint: disable=W0613
    """Implement your own validation logic to validate the input stanza configurations."""
    # This example accesses the modular input variable
    # global_account = definition.parameters.get('global_account', None)
    # outgoing_feeds = definition.parameters.get('outgoing_feeds', None)
    # domain = definition.parameters.get('domain', None)
    # ip = definition.parameters.get('ip', None)
    # uri = definition.parameters.get('uri', None)
    # filehash = definition.parameters.get('filehash', None)
    # email = definition.parameters.get('email', None)
    pass  # pylint: disable=W0107


def collect_events(helper, event_writer):  # pylint: disable=R0915
    """Implement your data collection logic here."""
    from collector.eiq_data import EIQApi  # pylint: disable=C0415

    stanza_names = helper.get_input_stanza()  # getting all stanza from inputs.conf
    input_stanza_name = helper.get_input_stanza_names()  # get current stanza name

    helper.log_info(CURRENT_INPUT_STANZA.format(input_stanza_name))

    host_name = stanza_names[input_stanza_name][GLOBAL_ACCOUNT][URL]
    helper.log_info(host_name)

    verify_ssl = False

    global_account = helper.get_arg(GLOBAL_ACCOUNT)
    api_key = global_account.get(API_KEY)
    verify_ssl = global_account.get(VERIFY_SSL)
    helper.log_info(verify_ssl)
    if verify_ssl and verify_ssl == "0":
        verify_ssl = False
    elif verify_ssl and verify_ssl == "1":
        verify_ssl = True
    else:
        verify_ssl = False

    opt_outgoing_feeds = helper.get_arg(OUTGOING_FEEDS, input_stanza_name)
    feed_ids = opt_outgoing_feeds.split(",")
    helper.log_info(OUTGOING_FEED_IDS_SELECTED.format(feed_ids))

    opt_start_date = helper.get_arg(START_DATE, input_stanza_name)
    obs_index = helper.get_arg("obs_index", input_stanza_name)
    entity_index = helper.get_arg("entity_index", input_stanza_name)
    opt_domain = helper.get_arg(DOMAIN, input_stanza_name)
    opt_ip = helper.get_arg(IP, input_stanza_name)
    opt_uri = helper.get_arg(URI, input_stanza_name)
    opt_filehash = helper.get_arg(FILEHASH, input_stanza_name)
    opt_email = helper.get_arg(EMAIL, input_stanza_name)
    opt_port = helper.get_arg(PORT, input_stanza_name)

    observable_ingest_types = {}
    observable_ingest_types[DOMAIN] = opt_domain
    observable_ingest_types[IP] = opt_ip
    observable_ingest_types[URI] = opt_uri
    observable_ingest_types[FILEHASH] = opt_filehash
    observable_ingest_types[EMAIL] = opt_email
    observable_ingest_types[PORT] = opt_port

    config_details = {}

    config_details[STANZA] = input_stanza_name
    config_details[HOST_NAME] = host_name
    config_details["verify_ssl"] = verify_ssl
    config_details[API_KEY] = api_key
    config_details[OUTGOING_FEEDS] = feed_ids
    config_details[START_DATE] = opt_start_date
    config_details["obs_index"] = obs_index
    config_details["entity_index"] = entity_index

    config_details[OBSERVABLE_INGEST_TYPES] = observable_ingest_types
    # Fetching proxy data
    proxy_settings = helper.get_proxy()
    helper.log_info(proxy_settings)

    helper.log_info(
        cli.getConfStanza(ADDITIONAL_PARAMTERS_CONFIG, ADDITIONAL_PARAMTERS_STANZA)
    )
    configs = cli.getConfStanza(
        ADDITIONAL_PARAMTERS_CONFIG, ADDITIONAL_PARAMTERS_STANZA
    )
    config_details[ADDITIONAL_PARAM_PAGE_SIZE] = (
        int(float(configs.get(ADDITIONAL_PARAM_PAGE_SIZE)))
        if configs.get(ADDITIONAL_PARAM_PAGE_SIZE)
        else DEFAULT_PAGE_SIZE
    )
    config_details[ADDITIONAL_PARAM_NUMBER_OF_RETRIES] = (
        int(float(configs.get(ADDITIONAL_PARAM_NUMBER_OF_RETRIES)))
        if configs.get(ADDITIONAL_PARAM_NUMBER_OF_RETRIES)
        else DEFAULT_NUMBER_OF_RETRIES
    )
    config_details[ADDITIONAL_PARAM_SLEEP_TIME] = (
        int(float(configs.get(ADDITIONAL_PARAM_SLEEP_TIME)))
        if configs.get(ADDITIONAL_PARAM_SLEEP_TIME)
        else DEFAULT_SLEEP_TIME
    )

    helper.log_info(config_details)

    try:
        eiq_api = EIQApi(helper, event_writer)
        eiq_api.get_observables(config_details, proxy_settings)
    except Exception as error:
        helper.log_info(error)
