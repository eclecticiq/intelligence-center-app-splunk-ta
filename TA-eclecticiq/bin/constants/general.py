"""General constants."""


APP_NAME = "TA-eclecticiq"
NOBODY = "nobody"  # nosec
SESSION_KEY = "session_key"  # nosec

# APIs
LIMIT = "limit"
OFFSET = "offset"
FILTER_LAST_UPDATED_AT = "filter[>last_updated_at]"
FILTER_OUTGOING_FEEDS = "filter[outgoing_feeds]"
SORT = "sort"
FILTER = "filter"
DATA = "data"
COUNT = "count"
PAYLOAD = "payload"
STATUS_STR = "status"
HEADERS = "headers"
AUTHORIZATION = "Authorization"

BEARER_TOKEN = "BEARER_TOKEN"  # nosec
NO_AUTH = "NO_AUTH"  # nosec
API_KEY = "api_key"
HOST_NAME = "host_name"

#
GET = "GET"

# Configs
TIMEOUT = "timeout"
MAX_RETRY = "max_retry"
RETRY_INTERVAL = "retry_interval"
VERIFY_SSL = "VERIFY_SSL"
PAGE_SIZE = "PAGE_SIZE"


# Observable data keys


DESC_BY_LAST_UPDATED_AT = "-last_updated_at"
MALICIOUSNESS = "maliciousness"

META = "meta"
VERSION_1 = "v1"
RANGE = "RANGE"

OBSERVABLES = "observables"

# General Constants

PLUS = "+"
SLASH = "/"
UNDERSCORE = "_"
STR_FIVE = "5"

# Status code
STATUS_CODE_500 = 500
STATUS_CODE_400 = 400
STATUS_CODE_404 = 404
STATUS_CODE_401 = 401
STATUS_CODE_403 = 403
STATUS_CODE_200 = 200
STATUS_CODE_201 = 201
STATUS_CODE_202 = 202
STATUS_CODE_422 = 422
STATUS_CODE_409 = 409


CREATED_AT = "created_at"
ID = "id"
LAST_UPDATED_AT = "last_updated_at"
VALUE = "value"
TYPE = "type"
ENTITY_ID = "entity_id"

STANZA = "stanza"

# kv store fields
CONFIDENCE_EIQ = "confidence_eiq"
_KEY = "_key"
_EIQ = "_eiq"
LAST_UPDATED_AT_EIQ = "last_updated_at_eiq"
OBSERVABLE_TIME_TO_LIVE = "observable_time_to_live"
TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%f%z"

# config details
OBSERVABLE_INGEST_TYPES = "observable_ingest_types"
START_DATE = "start_date"
OUTGOING_FEEDS = "outgoing_feeds"

DOMAIN = "domain"
EMAIL = "email"
PORT = "port"
IP = "ip"
URI = "uri"
FILEHASH = "filehash"
URL = "url"
GLOBAL_ACCOUNT = "global_account"
VERIFY_SSL = "certificate_validation"

ENTITY_TYPE = "entity_type"
ENTITY_RELEVANCY = "entity_relevancy"
RELEVANCY = "relevancy"
ENTITY_SOURCES = "entity_sources"
SOURCES = "sources"
ENTITY_DATA_TITLE = "entity_data_title"
DATA = "data"
TITLE = "title"
ENTITY_DATA_CONFIDENCE = "enity_data_confidence"
CONFIDENCE = "confidence"
META_TLP = "meta_tlp"
META_ESTIMATED_OBSERVED_TIME = "meta_estimated_observed_time"
META_ESTIMATED_THREAT_START_TIME = "meta_estimated_threat_start_time"
META_ESTIMATED_THREAT_END_TIME = "meta_estimated_threat_end_time"
META_TAGS = "meta_tags"
META_TAXONOMIES = "meta_taxonomies"
META_SOURCE_RELIABILITY = "meta_source_reliability"
FEED_ID = "feed_id"
OBSERVABLES = "observables"
OBSERVABLE_IDS = "observable_ids"

TLP_COLOR = "tlp_color"
ESTIMATED_OBSERVED_TIME = "estimated_observed_time"
ESTIMATED_THREAT_START_TIME = "estimated_threat_start_time"
ESTIMATED_THREAT_END_TIME = "estimated_threat_end_time"
TAGS = "tags"
TAXONOMIES = "taxonomies"
SOURCE_RELIABILITY = "source_reliability"

# Observable store
OBSERVABLE_STORE_COLLECTION_NAME = "test_eiq_obs"
ENTITIES_STORE_COLLECTION_NAME = "test_eiq_entities"

# Proxy Formatter paramters
PROXY_TYPE_HTTPS = "https"
PROXY_TYPE_HTTP = "http"
PROXY_TYPE = "proxy_type"
PROXY_URL = "proxy_url"
PROXY_PORT = "proxy_port"
PROXY_USERNAME = "proxy_username"  # nosec
PROXY_PASSWORD = "proxy_password"  # nosec

STR_COLON = ":"
CREDS = "creds"
PROXY = "proxy"


# Splunk rest realm
REST_REALM = "__REST_CREDENTIAL__#{app}#configs/conf-{conf}"

# HTTP METHODS
HTTPS = "https://"
POST = "POST"
GET = "GET"

# API
AUTHORIZATION = "Authorization"
CONTENT_TYPE = "Content-Type"
APPLICATION_JSON = "application/json"
ALERT_URL_FORMAT = "{serveraddress}/core/api-ua/alerts?key={api_key}&category={category}&Page={pagenumber}&size={pagesize}"

# Categories
DATA_LEAK = "Data_Leak"

# API configuration parameters
API_URL = "url"
API_KEY = "api_key"
START_DATE = "start_date"

# Response keys
BODY = "body"
EVENTS = "events"
MESSAGE = "message"


# Query Prameters
PARAM_START_TIME = "start_time"
PARAM_END_TIME = "end_time"
PARAM_ORDERTING = "ordering"
PARAM_PAGE_SIZE = "page_size"
PARAM_CURSOR = "cursor"

STR_ONE = "1"
STR_TILT = "`"
STR_EMPTY_JSON = "{}"
STR_EMPTY = ""
STR_COLON = ":"
STR_COMMA = ","
STR_AT_THE_RATE = "@"
DOMAIN_SEPERATOR = "://"

# Permissions for EIQ platform
READ_ENTITIES = "read entities"
MODIFY_EXTRACTS = "modify entities"
READ_EXTRACTS = "read extracts"
READ_OUTGOING_FEEDS = "read outgoing-feeds"
READ_PERMSSIONS = "read permissions"
TIME_MILLISECOND = 1000

NAME = "name"
SELF = "self"
PERMISSIONS = "permissions"

MIN_INTERVAL = 60
MAX_INTERVAL = 7776000


# Search parameters to remove duplication
EARLIEST_TIME = "earliest_time"
LATEST_TIME = "latest_time"
RESULT_COUNT = "resultCount"
EXEC_MODE = "exec_mode"