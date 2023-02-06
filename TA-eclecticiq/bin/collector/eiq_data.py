"""Entity and Observable collection APIs."""
import functools
import json

import time
from constants.defaults import (
    ADDITIONAL_PARAM_NUMBER_OF_RETRIES,
    ADDITIONAL_PARAM_SLEEP_TIME,
    DEFAULT_LIMIT,
    ENTITY_SOURCETYPE,
    OBS_SOURCETYPE
)

from utils.convertors import get_current_time
from utils.formatters import send_request
from splunk_apis.splunk_api import SplunkApi

from constants.eiq_api import (  # pylint: disable=C0412
    EIQ_ENTITIES,
    EIQ_OBSERVABLES_BY_ID,
)
from constants.general import (  # pylint: disable=C0412
    _EIQ,
    _KEY,
    API_KEY,
    CONFIDENCE,
    COUNT,
    DATA,
    DESC_BY_LAST_UPDATED_AT,
    ENTITY_DATA_CONFIDENCE,
    ENTITY_DATA_TITLE,
    ENTITY_ID,
    ENTITY_RELEVANCY,
    ENTITY_SOURCES,
    ENTITY_TYPE,
    ESTIMATED_OBSERVED_TIME,
    ESTIMATED_THREAT_END_TIME,
    ESTIMATED_THREAT_START_TIME,
    FEED_ID,
    FILTER_LAST_UPDATED_AT,
    FILTER_OUTGOING_FEEDS,
    HOST_NAME,
    ID,
    LIMIT,
    META,
    META_ESTIMATED_OBSERVED_TIME,
    META_ESTIMATED_THREAT_END_TIME,
    META_ESTIMATED_THREAT_START_TIME,
    META_SOURCE_RELIABILITY,
    META_TAGS,
    META_TAXONOMIES,
    META_TLP,
    OBSERVABLE_IDS,
    OBSERVABLE_INGEST_TYPES,
    OBSERVABLES,
    OFFSET,
    OUTGOING_FEEDS,
    PLUS,
    RELEVANCY,
    SLASH,
    SORT,
    SOURCE_RELIABILITY,
    SOURCES,
    STANZA,
    START_DATE,
    STATUS_CODE_200,
    STATUS_CODE_201,
    TAGS,
    TAXONOMIES,
    TITLE,
    TLP_COLOR,
    TYPE,
    UNDERSCORE,
    LAST_UPDATED_AT_EIQ,
    STR_COMMA,
    STR_EMPTY
)
from constants.messages import (  # pylint: disable=C0412
    BREAK_LOOP,
    CHECKPOINT_FOUND,
    CHECKPOINT_SUCCESSFULLY_WRITTEN,
    COLLECTING_DATA,
    COLLECTING_OBSERVABLE,
    DATA_FOUND_FOR_FEED_ID_AND_TYPE,
    ENDPOINT_CALLED,
    ENTITY_ID_AND_OBSERVABLE_IDS,
    GET_OBSERVABLE,
    GET_OBSERVABLE_DATA,
    IN_GET_ENTITIES,
    JSON_EXCEPTION,
    MAX_RETRY_WARNING,
    NOT_LOADING_OBSERVABLE,
    OBSERVABLE_TYPE_MODIFIED,
    OBSERVABLE_TYPE_RECEIVED,
    OBSERVABLES_AND_CHECKPOINT_RECEIVED,
    OUTGOING_FEED_ID,
    PENDING_OBSERVABLES,
    RESPONSE_RECEIVED,
    RETRY_ERROR_MSG,
    SEND_REQUEST,
    WRITING_CHECKPOINT,
    INSERTING_ENTITY_WITH_ID,
    RESPONSE_RECEIVED_IS,
    SUCCESSFULLY_INSERTED_ENTITY
)


def retry():
    """Get Wrapper for retrying the request multiple times.

    :param num_attempts: Number of attempts to be made, defaults to 3
    :type num_attempts: int, optional
    :param exception_class: Exception to be throuwn in case of failure,
                            defaults to Exception
    :type exception_class: object, optional
    :param sleeptime: Wait time between consecutive retries, defaults to 1
    :type sleeptime: int, optional
    :return: Wrapper function
    :rtype: object
    """
    # Decorator which helps to retry functions when an Exceptions occurred
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            helper_method = args[0].helper
            input_name = str(helper_method.get_input_stanza_names())

            num_attempts = args[-2]
            sleeptime = args[-1]
            for attempt in range(num_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception:  # pragma: no cover
                    if attempt == num_attempts - 1:
                        helper_method.log_warning(
                            MAX_RETRY_WARNING.format(input=input_name)
                        )
                        return {}

                    helper_method.log_warning(
                        RETRY_ERROR_MSG.format(input=input_name))
                    time.sleep(sleeptime)

        return wrapper

    return decorator


class EIQApi:
    """EIQ APIs for entity and observable collection."""

    def __init__(self, helper, event_writer):
        self.helper = helper
        self.event_writer = event_writer

    @staticmethod
    def get_unique_observables(data):
        """Get the unique observable ids from list of observable ids url.

        :param data: list of url observable ids
        :type data: list
        :return: observable_ids
        :rtype: set
        """
        observables = set()
        observable_list = data.get(OBSERVABLES)
        if observable_list:
            observables.update(set(observable_list))
        observables = EIQApi.get_observable_ids(observables)
        return observables

    @staticmethod
    def get_observable_ids(data):
        """Get the unique observable ids from list of observable ids url.

        :param data: list of url observable ids
        :type data: list
        :return: observable_ids
        :rtype: set
        """
        observable_ids = set()
        for item in data:
            observable_ids.add(str(item.split(SLASH)[-1]))
        return observable_ids

    def get_response_content(self, response):
        """Get the response content from the response.

        :param response: Response to retrieve content
        :type response: Response
        :return: Response content
        :rtype: dict / None
        """
        content = {}
        try:
            content = json.loads(response.content)
        except json.decoder.JSONDecodeError as error:
            self.helper.log_info(JSON_EXCEPTION.format(error))

        return content

    @staticmethod
    def check_observable_type(observable_type):
        """Check observable type.

        :param observable_type: observable_type
        :type observable_type: str
        :return: observable type
        :rtype: str
        """
        if observable_type in ["ipv4", "ipv6"]:
            observable_type = "ip"
        elif observable_type in ["hash-md5", "hash-sha1", "hash-sha256", "hash-sha512"]:
            observable_type = "filehash"

        return observable_type

    @staticmethod
    def get_observable_ingest_types(config_details):
        """Get observable ingest types.

        :param config_details: config_details
        :type config_details: dict
        :return: ingest types
        :rtype: list
                ['domain','ip']
        """
        observable_types = config_details[OBSERVABLE_INGEST_TYPES]
        ingest_types = [
            val for val in observable_types if observable_types[val]]
        return ingest_types

    def formatted_data_to_load(self, observable_data, config_details):
        """Get formatted data for observable to load in kv store.

        :param config_details: configuration details from input page
        :type config_details: dict
        :param entity_id: entity id
        :type entity_id: dict
        :param observable_data: observable data to format
        :type observable_data: dict
        :return: observable type, temporary dict to format
        :rtype: str, dict

        """
        observable_ingest_types = EIQApi.get_observable_ingest_types(
            config_details)
        observable_type = observable_data[TYPE]

        self.helper.log_info(OBSERVABLE_TYPE_RECEIVED.format(observable_type))
        obs_type = EIQApi.check_observable_type(observable_type)
        self.helper.log_info(OBSERVABLE_TYPE_MODIFIED.format(obs_type))
        if obs_type in observable_ingest_types:
            return observable_type, observable_data
        else:
            return observable_type, None

    @retry()
    def get_observable_data(
        self,
        observable_ids,
        outgoing_feed_id,
        entity_id,
        config_details,
        proxy_settings,
        num_attempts,  # pylint: disable=W0613
        sleeptime,  # pylint: disable=W0613
    ):
        """Get the observable data and  load in Splunk KV store.

        :param outgoing_feed_id: outgoing feed id
        :type outgoing_feed_id: str
        :param observable_ids: list of observable ids
        :type observable_ids: list
        :param entity_id: entity id
        :type entity_id: str
        :param config_details: configuration details received from input
        :type config_details: dict

        :return: response
        :rtype: boolean
        """
        self.helper.log_info(GET_OBSERVABLE)
        self.helper.log_info(
            ENTITY_ID_AND_OBSERVABLE_IDS.format(entity_id, observable_ids)
        )
        counter = 1

        for observable_id in observable_ids:
            self.helper.log_info(
                PENDING_OBSERVABLES.format(len(observable_ids) - counter)
            )
            self.helper.log_info(COLLECTING_OBSERVABLE.format(counter))
            self.helper.log_info(
                GET_OBSERVABLE_DATA.format(observable_id, outgoing_feed_id)
            )

            headers = {"Authorization": f"Bearer {config_details[API_KEY]}"}
            endpoint = EIQ_OBSERVABLES_BY_ID + SLASH + observable_id
            url = config_details[HOST_NAME] + endpoint
            self.helper.log_info(ENDPOINT_CALLED.format(url))
            try:
                response = send_request(
                    self.helper,
                    url=url,
                    headers=headers,
                    params=None,
                    proxy=proxy_settings,
                    configs=config_details,
                )
            except Exception:
                self.helper.log_info("Skipping this observable.")
                continue

            if response.status_code not in [STATUS_CODE_200, STATUS_CODE_201]:
                self.helper.log_info(
                    RESPONSE_RECEIVED.format(response.status_code))
                return False

            content = self.get_response_content(response)
            data = content.get(DATA)

            obs_type, observable_type_data = self.formatted_data_to_load(
                data, config_details
            )

            if observable_type_data:
                self.helper.log_info(
                    DATA_FOUND_FOR_FEED_ID_AND_TYPE.format(
                        outgoing_feed_id, obs_type
                    )
                )

                splunk_api = SplunkApi(self.helper, self.event_writer)
                OBSERVABLE_STORE_COLLECTION_NAME = config_details["obs_index"]
                response = splunk_api.insert_record_in_collection(
                    observable_type_data, OBS_SOURCETYPE, OBSERVABLE_STORE_COLLECTION_NAME, config_details[
                        HOST_NAME]
                )
                if not response:
                    return response
            else:
                self.helper.log_info(
                    NOT_LOADING_OBSERVABLE.format(data["type"]))
            counter += 1

        return True

    def get_entity_data(self, entities_data, feed_id, config_details, proxy_settings):
        """Get entity data and observable data and load formatted data in KV store.

        :param entities_data: entities data to load
        :type entities_data: dict
        :param feed_id: outgoing feed id
        :type feed_id: str
        :param config_details: configuration details received from input page
        :type config_details: dict

        :return: response
        :rtype: boolean
        """
        for data in entities_data:

            splunk_api = SplunkApi(self.helper, self.event_writer)
            response_observables = False
            response_entity = False

            entity_id = data[ID]
            self.helper.log_debug(entity_id)
            self.helper.log_info(INSERTING_ENTITY_WITH_ID.format(entity_id))
            data[OUTGOING_FEEDS] = feed_id
            ENTITIES_STORE_COLLECTION_NAME = config_details["entity_index"]
            response_entity = splunk_api.insert_record_in_collection(
                data, ENTITY_SOURCETYPE, ENTITIES_STORE_COLLECTION_NAME, config_details[
                    HOST_NAME]
            )
            self.helper.log_info(
                SUCCESSFULLY_INSERTED_ENTITY.format(entity_id))
            observable_ids = EIQApi.get_unique_observables(data)

            if observable_ids:
                response_observables = self.get_observable_data(
                    observable_ids,
                    feed_id,
                    entity_id,
                    config_details,
                    proxy_settings,
                    config_details[ADDITIONAL_PARAM_NUMBER_OF_RETRIES],
                    config_details[ADDITIONAL_PARAM_SLEEP_TIME],
                )
                # fetch data and insert in splunk index

            if (not response_observables) and (not response_entity):

                self.helper.log_info(
                    RESPONSE_RECEIVED_IS
                )
                return False

        return True

    @retry()
    def get_entities(
        self,
        headers,
        parameters,
        outgoing_feed_id,
        config_details,
        proxy_settings,
        num_attempts,  # pylint: disable=W0613
        sleeptime,  # pylint: disable=W0613
    ):
        """Get the entities from eiq and make list of observables.

        :param headers: headers for eiq apis
        :type headers: dict
        :param parameters: params required in apis
        :type parameters: dict
        :param parameters: params required in apis
        :type parameters: dict
        :param parameters: params required in apis
        :type parameters: dict

        :return: observables, new_checkpoint,response
        :rtype: observables list, checkpoint and response

        """
        observables = []
        new_checkpoint = None
        response = False
        counter = 0
        while True:

            counter += 1
            self.helper.log_info(IN_GET_ENTITIES.format(counter))
            self.helper.log_info(SEND_REQUEST.format(parameters))

            url = config_details[HOST_NAME] + EIQ_ENTITIES

            response = send_request(
                self.helper,
                url=url,
                params=parameters,
                headers=headers,
                proxy=proxy_settings,
                configs=config_details,
            )
            # self.helper.log_info(response.status_code)

            content = self.get_response_content(response)
            count = content.get(COUNT)

            if response.status_code not in [STATUS_CODE_200, STATUS_CODE_201]:
                self.helper.log_info(
                    RESPONSE_RECEIVED.format(response.status_code))
                self.helper.log_info(
                    RESPONSE_RECEIVED.format(str(response.content)))
                return observables, new_checkpoint, response

            data = content.get(DATA)  # Get entities for the lookup
            # self.helper.log_info(data)

            response = self.get_entity_data(
                data, outgoing_feed_id, config_details, proxy_settings
            )
            if not response:
                return observables, new_checkpoint, response

            if parameters.get(OFFSET):
                parameters[OFFSET] += parameters[LIMIT]
            else:
                parameters[OFFSET] = parameters[LIMIT]

            if count < parameters[LIMIT] or response == {}:
                self.helper.log_info(BREAK_LOOP)
                new_checkpoint = get_current_time()
                break
        return observables, new_checkpoint, response

    def get_observables(self, config_details, proxy_settings):
        """Get observable data and entities data from EIQ platform.

        :param config_details: configuration details received from input
        :type config_details: dict
        """
        self.helper.log_info(COLLECTING_DATA)
        outgoing_feeds_ids = config_details[OUTGOING_FEEDS]

        for outgoing_feed in outgoing_feeds_ids:
            self.helper.log_info(OUTGOING_FEED_ID.format(outgoing_feed))

            checkpoint_name = config_details[STANZA] + \
                UNDERSCORE + str(outgoing_feed)
            checkpoint = self.helper.get_check_point(checkpoint_name)

            start_date = config_details[START_DATE]
            if checkpoint:
                self.helper.log_info(CHECKPOINT_FOUND.format(outgoing_feed))
                start_date = checkpoint

            headers = {"Authorization": f"Bearer {config_details[API_KEY]}"}

            parameters = {
                LIMIT: DEFAULT_LIMIT,
                FILTER_LAST_UPDATED_AT: start_date,
                FILTER_OUTGOING_FEEDS: str(outgoing_feed),
                SORT: DESC_BY_LAST_UPDATED_AT,
            }
            response = True

            observables, new_checkpoint, response = self.get_entities(
                headers,
                parameters,
                outgoing_feed,
                config_details,
                proxy_settings,
                config_details[ADDITIONAL_PARAM_NUMBER_OF_RETRIES],
                config_details[ADDITIONAL_PARAM_SLEEP_TIME],
            )
            self.helper.log_info(
                OBSERVABLES_AND_CHECKPOINT_RECEIVED.format(
                    len(observables), new_checkpoint
                )
            )

            if new_checkpoint and response:
                new_checkpoint = new_checkpoint.split(PLUS)
                new_checkpoint = new_checkpoint[0]
                self.helper.log_info(WRITING_CHECKPOINT.format(new_checkpoint))
                self.helper.save_check_point(checkpoint_name, new_checkpoint)
                self.helper.log_info(CHECKPOINT_SUCCESSFULLY_WRITTEN)

            time.sleep(0.2)
