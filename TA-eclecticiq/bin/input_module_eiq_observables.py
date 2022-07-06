# encoding = utf-8
"""Input module for entity and observable collection."""

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
    STANZA,
    START_DATE,
    URI,
    URL,
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


def collect_events(helper, event_writer):
    """Implement your data collection logic here."""
    from collector.eiq_data import EIQApi  # pylint: disable=C0415

    stanza_names = helper.get_input_stanza()  # getting all stanza from inputs.conf
    input_stanza_name = helper.get_input_stanza_names()  # get current stanza name

    helper.log_info(CURRENT_INPUT_STANZA.format(input_stanza_name))

    host_name = stanza_names[input_stanza_name][GLOBAL_ACCOUNT][URL]

    global_account = helper.get_arg(GLOBAL_ACCOUNT)
    api_key = global_account.get(API_KEY)

    opt_outgoing_feeds = helper.get_arg(OUTGOING_FEEDS, input_stanza_name)
    feed_ids = opt_outgoing_feeds.split(",")
    helper.log_info(OUTGOING_FEED_IDS_SELECTED.format(feed_ids))

    opt_start_date = helper.get_arg(START_DATE, input_stanza_name)

    opt_domain = helper.get_arg(DOMAIN, input_stanza_name)
    opt_ip = helper.get_arg(IP, input_stanza_name)
    opt_uri = helper.get_arg(URI, input_stanza_name)
    opt_filehash = helper.get_arg(FILEHASH, input_stanza_name)
    opt_email = helper.get_arg(EMAIL, input_stanza_name)

    observable_ingest_types = {}
    observable_ingest_types[DOMAIN] = opt_domain
    observable_ingest_types[IP] = opt_ip
    observable_ingest_types[URI] = opt_uri
    observable_ingest_types[FILEHASH] = opt_filehash
    observable_ingest_types[EMAIL] = opt_email

    config_details = {}

    config_details[STANZA] = input_stanza_name
    config_details[HOST_NAME] = host_name
    config_details[API_KEY] = api_key
    config_details[OUTGOING_FEEDS] = feed_ids
    config_details[START_DATE] = opt_start_date

    config_details[OBSERVABLE_INGEST_TYPES] = observable_ingest_types
    # Fetching proxy data
    proxy_settings = helper.get_proxy()
    helper.log_info(config_details)
    try:
        eiq_api = EIQApi(helper, event_writer)
        eiq_api.get_observables(config_details, proxy_settings)
    except Exception as error:
        helper.log_info(error)
