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
        default="3600",
        validator=validator.Number(
            min_val=1, 
            max_val=7776000, 
        ),
    ),
    field.RestField(
        "observable_time_to_live",
        required=True,
        encrypted=False,
        default="90",
        validator=validator.Number(
            min_val=1, 
            max_val=90, 
        ),
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
