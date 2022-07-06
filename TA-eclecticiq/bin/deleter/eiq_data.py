"""Entity and observable deletion APIs."""
from splunk_apis.splunk_api import SplunkApi
from utils.convertors import get_formatted_date
from constants.general import (
    _KEY,
    ENTITIES_STORE_COLLECTION_NAME,
    ENTITY_ID,
    LAST_UPDATED_AT_EIQ,
    OBSERVABLE_IDS,
    OBSERVABLE_STORE_COLLECTION_NAME,
    OBSERVABLE_TIME_TO_LIVE,
    PLUS,
)
from constants.messages import (
    DELETE_OBSERVABLE_DATA_IS_OLDER,
    DELETE_OBSERVABLES,
    DELETE_OBSERVABLES_DATA_NOT_OLDER,
    ENTITY_ID_RECEIVED_FOR_DELETE_OBSERVABLES,
    LAST_UPDATED_VALUE_NOT_FOUND,
    LENGTH_ENTITY_ID_LESS_THAN_2,
)


class EIQDeleterApi:
    """EIQ APIs for observable and entity deletion."""

    def __init__(self, helper, event_writer):
        self.helper = helper
        self.event_writer = event_writer

    def initiate_delete_observables(self, observable_time_to_live):
        """Delete observables from splunk kv store.

        :param observable_time_to_live: observable time to live in days
        :type observable_time_to_live: str
        :return: response
        :rtype: boolean

        """
        observable_time_to_live = get_formatted_date(int(observable_time_to_live))
        self.helper.log_info(OBSERVABLE_TIME_TO_LIVE.format(observable_time_to_live))
        splunk_api = SplunkApi(self.helper, self.event_writer)
        response = splunk_api.get_all_records_in_collection(
            OBSERVABLE_STORE_COLLECTION_NAME
        )
        content = response
        response = False

        for data in content:

            self.helper.log_info(DELETE_OBSERVABLES)
            last_updated_at_value = (
                data.get(LAST_UPDATED_AT_EIQ) if data.get(LAST_UPDATED_AT_EIQ) else None
            )
            observable_id = data.get(_KEY)

            if not last_updated_at_value:
                self.helper.log_info(LAST_UPDATED_VALUE_NOT_FOUND.format(data[_KEY]))
                continue

            last_updated_at = last_updated_at_value.split(PLUS)[0]
            self.helper.log_info(last_updated_at)
            if last_updated_at <= observable_time_to_live:
                self.helper.log_info(
                    DELETE_OBSERVABLE_DATA_IS_OLDER.format(
                        last_updated_at, observable_time_to_live
                    )
                )

                # get the entity id
                entity_id = data.get(ENTITY_ID)
                self.helper.log_info(
                    ENTITY_ID_RECEIVED_FOR_DELETE_OBSERVABLES.format(entity_id)
                )
                if len(entity_id) < 2:
                    # delete the entity
                    self.helper.log_info(LENGTH_ENTITY_ID_LESS_THAN_2.format(entity_id))
                    response = splunk_api.delete_record_from_collection(
                        ENTITIES_STORE_COLLECTION_NAME, entity_id
                    )
                else:
                    # get the entity id data
                    # update the entityid with the observable value removed
                    entity_ids_list = entity_id.split(",")
                    for entity_id in entity_ids_list:
                        response = splunk_api.get_record_in_collection(
                            ENTITIES_STORE_COLLECTION_NAME, entity_id
                        )
                        content = response[0]
                        observable_ids = content[OBSERVABLE_IDS].split(",")

                        if observable_id in observable_ids:
                            observable_ids.remove(observable_id)

                        content[OBSERVABLE_IDS] = ",".join(observable_ids)
                        response = splunk_api.update_record_in_collection(
                            content, ENTITIES_STORE_COLLECTION_NAME, entity_id
                        )
                        self.helper.log_info("Record is updated in eiq_entities_list")

                # delete the observable
                if response:
                    response = splunk_api.delete_record_from_collection(
                        OBSERVABLE_STORE_COLLECTION_NAME, observable_id
                    )

                if not response:
                    return response

            else:
                self.helper.log_info(
                    DELETE_OBSERVABLES_DATA_NOT_OLDER.format(
                        last_updated_at, observable_time_to_live
                    )
                )

        return response
