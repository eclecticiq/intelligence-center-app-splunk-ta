import ta_eclecticiq_declare
from validator.validate import ValidateAccount

from splunktaucclib.rest_handler.endpoint import (
    field,
    validator,
    RestModel,
    SingleModel,
)
from splunktaucclib.rest_handler import admin_external, util
from splunk_aoblib.rest_migration import ConfigMigrationHandler

util.remove_http_proxy_env_vars()

fields = [
    field.RestField(
        "api_key",
        required=True,
        encrypted=True,
        default=None,
        validator=validator.String(
            min_len=1,
            max_len=8192,
        ),
    ),
    field.RestField(
        "url",
        required=True,
        encrypted=False,
        default=None,
        validator=ValidateAccount()
    ),
]
model = RestModel(fields, name=None)

endpoint = SingleModel(
    "ta_eclecticiq_account",
    model,
)

if __name__ == "__main__":
    admin_external.handle(
        endpoint,
        handler=ConfigMigrationHandler,
    )
