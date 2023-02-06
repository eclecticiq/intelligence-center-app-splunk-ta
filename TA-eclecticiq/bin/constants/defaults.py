"""Default constants ."""

DEFAULT_LIMIT = 200
DEFAULT_TIMEOUT = 300
DEFAULT_MAX_RETRY = 3
DEFAULT_RETRY_INTERVAL = 15
DEFAULT_VERIFY_SSL = True
DEFAULT_PAGE_SIZE = 10

DEFAULT_SCHEDULER_INTERVAL = 3600

DEFAULT_LOWER_LIMIT = 0
DEFAULT_UPPER_LIMIT = 5000

DEFAULT_INDICATOR_TYPE = "all"
DEFAULT_CONFIDENCE_LEVEL = "high"
DEFAULT_TIME = "24h"


# Default ordering paramter value
DEFAULT_NUMBER_OF_RETRIES = 3


# Conf files

ACCOUNTS_CONF = "ta_eclecticiq_account.conf"
SETTINGS_CONF = "ta_eclecticiq_settings.conf"
LOCAL_DIR = "local"
ENTITY_SOURCETYPE = "eiq:ic:entities"
OBS_SOURCETYPE = "eiq:ic:observables"

# Additional Conf parameters
ADDITIONAL_PARAMTERS_CONFIG = "ta_eclecticiq_settings"
ADDITIONAL_PARAMTERS_STANZA = "additional_parameters"
ADDITIONAL_PARAM_NUMBER_OF_RETRIES = "number_of_retries"
ADDITIONAL_PARAM_PAGE_SIZE = "page_size"
ADDITIONAL_PARAM_SLEEP_TIME = "sleep_time"


# Default delete original key in mapping
DEFAULT_SLEEP_TIME = 100


# Search data in indexes to handle duplication
SEARCH_RECORDS_QUERY = 'search index="{}" sourcetype="{}" | search id={} | sort -last_updated_at | head 1'
DEFAULT_EARLIEST_TIME = "0"
DEFAULT_LATEST_TIME = "now"
DEFAULT_EXEC_MODE = "blocking"