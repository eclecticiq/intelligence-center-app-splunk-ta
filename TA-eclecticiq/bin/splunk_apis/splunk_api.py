"""Splunk APIs for KV store."""

import json
import traceback
from constants.defaults import (
    DEFAULT_EARLIEST_TIME,
    DEFAULT_EXEC_MODE,
    DEFAULT_LATEST_TIME,
    SEARCH_RECORDS_QUERY,
)
from constants.general import (
    EARLIEST_TIME,
    EXEC_MODE,
    ID,
    LAST_UPDATED_AT,
    LATEST_TIME,
    RESULT_COUNT,
    STR_ONE,
    TIME_FORMAT,
    _KEY,
    APP_NAME,
    NOBODY,
    SESSION_KEY,
)
from constants.messages import (
    INSERTING_EVENT_WITH_ID,
    NO_EVENTS_FOUND_INSERTING,
    NOT_INSERTING_EVENT_WITH_ID,
)
import splunklib.client as client
from splunklib.binding import HTTPError
import datetime
from datetime import timezone
import splunklib.results as results


class SplunkApi:
    """Splunk APIs for KV Store."""

    def __init__(self, helper, event_writer):
        self.helper = helper
        self.event_writer = event_writer

    def insert_record_in_collection(self, data, sourcetype, collection_name, source):
        """Insert record in  splunk kv store.

        :param data: data to insert in collection
        :type data: dict
        :param collection_name: collection name to insert the data
        :type collection_name: str

        :return: response
        :rtype: boolean
        """
        try:
            insertion = True
            session_key = self.helper.context_meta[SESSION_KEY]
            # self.helper.log_info("session_key ={}".format(session_key))
            service = client.connect(token=session_key, owner=NOBODY, app=APP_NAME)
            # self.helper.log_info("service created!")
            query = SEARCH_RECORDS_QUERY.format(collection_name, sourcetype, data[ID])
            # Create a search job
            kwargs_oneshotsearch = {
                EARLIEST_TIME: DEFAULT_EARLIEST_TIME,
                LATEST_TIME: DEFAULT_LATEST_TIME,
                EXEC_MODE: DEFAULT_EXEC_MODE,
            }
            job = service.jobs.create(query, **kwargs_oneshotsearch)
            job_stats = job.content
            if job_stats.get(RESULT_COUNT) and job_stats.get(RESULT_COUNT) == STR_ONE:
                search_results = results.ResultsReader(job.results())
                result_list = {}
                for result in search_results:
                    result_list = json.loads(json.dumps(result))
                self.helper.log_info(result_list)
                if result_list:
                    if data[LAST_UPDATED_AT] > result_list[LAST_UPDATED_AT]:
                        insertion = True
                        self.helper.log_info(INSERTING_EVENT_WITH_ID.format(data[ID]))
                    else:
                        self.helper.log_info(
                            NOT_INSERTING_EVENT_WITH_ID.format(data[ID])
                        )
                        insertion = False
                else:
                    self.helper.log_info(NO_EVENTS_FOUND_INSERTING.format(data[ID]))
                    insertion = True
            else:
                self.helper.log_info(NO_EVENTS_FOUND_INSERTING.format(data[ID]))
                insertion = True

            if insertion:
                seconds = 1
                time_field = datetime.datetime.strptime(
                    data[LAST_UPDATED_AT], TIME_FORMAT
                )
                epoch_time = int(
                    time_field.replace(tzinfo=timezone.utc).timestamp() * seconds
                )
                splnk_event = self.helper.new_event(
                    source=source,
                    index=collection_name,
                    sourcetype=sourcetype,
                    data=json.dumps(data),
                    time=epoch_time,
                )
                self.event_writer.write_event(splnk_event)
            return True
        except Exception:
            self.helper.log_info(traceback.format_exc())
            return False
