import ta_eclecticiq_declare
from validator.validate_deletion import ValidateDeletion
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
        validator=None,
    ),
    field.RestField(
        "observable_time_to_live",
        required=True,
        encrypted=False,
        default="90",
        validator=ValidateDeletion(),
    ),
    field.RestField("disabled", required=False, validator=None),
]
model = RestModel(fields, name=None)

endpoint = DataInputModel(
    "eiq_observables_deletion",
    model,
)

if __name__ == "__main__":
    admin_external.handle(
        endpoint,
        handler=ConfigMigrationHandler,
    )
