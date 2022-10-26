"""Input module for entity and observable deletion."""
# encoding = utf-8


from constants.general import OBSERVABLE_TIME_TO_LIVE
from constants.messages import (
    ALL_OBSERVABLES_SUCCESSFULLY_DELETED,
    UNABLE_TO_DELETE_OBSERVABLES,
)


def validate_input(helper, definition):  # pylint: disable=W0613
    """Implement your own validation logic to validate the input stanza configurations."""
    # This example accesses the modular input variable
    # observable_time_to_live = definition.parameters.get('observable_time_to_live', None)
    pass  # pylint: disable=W0107


def collect_events(helper, event_writer):
    """Implement your data collection logic here."""
    from deleter.eiq_data import EIQDeleterApi  # pylint: disable=C0415

    input_stanza_name = helper.get_input_stanza_names()  # get current stanza name

    opt_observable_time_to_live = helper.get_arg(
        OBSERVABLE_TIME_TO_LIVE, input_stanza_name
    )
    helper.log_debug(input_stanza_name)
    helper.log_debug(opt_observable_time_to_live)

    eiq_api = EIQDeleterApi(helper, event_writer)
    response = eiq_api.initiate_delete_observables(opt_observable_time_to_live)

    if not response:
        helper.log_info(UNABLE_TO_DELETE_OBSERVABLES)
    helper.log_info(ALL_OBSERVABLES_SUCCESSFULLY_DELETED)
