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

# config details
OBSERVABLE_INGEST_TYPES = "observable_ingest_types"
START_DATE = "start_date"
OUTGOING_FEEDS = "outgoing_feeds"

DOMAIN = "domain"
EMAIL = "email"
IP = "ip"
URI = "uri"
FILEHASH = "filehash"
URL = "url"
GLOBAL_ACCOUNT = "global_account"

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
OBSERVABLE_STORE_COLLECTION_NAME = "eiq_ioc_list"
ENTITIES_STORE_COLLECTION_NAME = "eiq_entities_list"

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
