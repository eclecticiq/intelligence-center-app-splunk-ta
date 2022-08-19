"""Constant for create sighting right click actions."""


DATA_STR = "data"
TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"
TEXT_PLAIN = "text/plain"
INPUT_NAME = "create_sighting"
CONTENT_TYPE = "Content-Type"
VALUE = "value"
SIGHTING_VALUE = "sighting_value"
DESCRIPTION = "description"
SIGHTING_DESC = "sighting_desc"
TIMESTAMP_STR = "timestamp"
CONFIDENCE = "confidence"
CONFIDENCE_LEVEL = "confidence_level"
TITLE = "title"
SIGHTING_TITLE = "sighting_title"
SIGHTING_TAGS = "sighting_tags"
TAGS = "tags"
META = "meta"
SECURITY_CONTROL = "security_control"
TYPE = "type"
SIGHTING_TYPE = "sighting_type"
TIME = "time"
START_TIME = "start_time"
INGEST_TIME = "ingest_time"

SIGHTING_SCHEMA = {
    "data": {
        "data": {
            "value": "value",
            "confidence": "medium",
            "description": "test_desc",
            "type": "eclecticiq-sighting",
            "timestamp": "",
            "title": "title1",
            "security_control": {
                "type": "information-source",
                "identity": {
                    "name": "EclecticIQ Platform Add-on for Splunk",
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
