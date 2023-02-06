from validator.validate_inputs import ValidateInputs
import ta_eclecticiq_declare

from splunktaucclib.rest_handler.endpoint import (
    field,
    validator,
    RestModel,
    DataInputModel,
)
from splunktaucclib.rest_handler import admin_external, util
from splunk_aoblib.rest_migration import ConfigMigrationHandler

util.remove_http_proxy_env_vars()

fields = [
    field.RestField(
        "interval",
        required=True,
        encrypted=False,
        default=None
    ),
    field.RestField(
        "global_account", required=True, encrypted=False, default=None, validator=None
    ),
    field.RestField(
        "outgoing_feeds",
        required=True,
        encrypted=False,
        default=None,
        validator=validator.String(
            min_len=1,
            max_len=8192,
        ),
    ),
    field.RestField(
        "obs_index", required=False, encrypted=False, default=None, validator=None
    ),
    field.RestField(
        "entity_index", required=False, encrypted=False, default=None, validator=None
    ),
    field.RestField(
        "domain", required=False, encrypted=False, default=None, validator=None
    ),
    field.RestField(
        "ip", required=False, encrypted=False, default=None, validator=None
    ),
    field.RestField(
        "uri", required=False, encrypted=False, default=None, validator=None
    ),
    field.RestField(
        "filehash", required=False, encrypted=False, default=None, validator=None
    ),
    field.RestField(
        "email", required=False, encrypted=False, default=None, validator=None
    ),
    field.RestField(
        "port", required=False, encrypted=False, default=None, validator=None
    ),
    field.RestField(
        "start_date", required=True, encrypted=False, default=None, validator=ValidateInputs()
    ),
    field.RestField("disabled", required=False, validator=None),
]
model = RestModel(fields, name=None)

endpoint = DataInputModel(
    "eiq_observables",
    model,
)

if __name__ == "__main__":
    admin_external.handle(
        endpoint,
        handler=ConfigMigrationHandler,
    )
