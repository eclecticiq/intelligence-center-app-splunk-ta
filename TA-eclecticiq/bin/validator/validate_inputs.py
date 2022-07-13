"""Validate Inputs."""
import os
import splunk.admin as admin

import datetime


from splunktaucclib.rest_handler.endpoint.validator import Validator
from validator.logger_manager import setup_logging

from constants.general import (
    DOMAIN,
    EMAIL,
    FILEHASH,
    IP,
    MAX_INTERVAL,
    MIN_INTERVAL,
    PORT,
    START_DATE,
    URI,
    URL,
)

from constants.messages import (
    BACKFILL_TIME_OLDER,
    INTERVAL_MUST_BE_BETWEEN_MIN_AND_MAX_INTERVAL,
    MIN_AND_MAX_INTERVAL,
    SELECT_ATLEAST_ONE_OBSERVABLE_TYPE,
    SELECT_ATLEAST_ONE_OBSERVABLE_TYPE_TO_BE_INGESTED,
    START_DATE_NOT_VALID_FORMAT,
)
from constants.general import STR_ONE


logger = setup_logging("ta_eclecticiq_inputs")


class GetSessionKey(admin.MConfigHandler):  # type: ignore
    """Inheriting admin.MConfigHandler to get the current user's session key."""

    def __init__(self):
        """Set the session key as parameter to use while getting entities from Splunk REST."""
        self.session_key = self.getSessionKey()


class ValidateInputs(Validator):  # type: ignore
    """Inheriting the Validator Class for creating custom validations."""

    def __init__(self, *args, **kwargs):  # pylint: disable=W0613
        """Create instance of ValidateAccount class along with Super class parameters Setting the my_app parameter as main TA directory name."""
        super().__init__()
        self.my_app = __file__.split(os.sep)[-4]

    @staticmethod
    def check_start_date_days(backfill_date):
        """Check Start date provided by user is not more than 90 days.

        :param backfill_date: datetime
        :type backfill_date: str
        :return: True if the date is not older than 90 days else False
        :rtype: boolean
        """
        start_date = datetime.datetime.strptime(backfill_date, "%Y-%m-%dT%H:%M:%S.%f")
        current_date = datetime.datetime.now()
        backfill_time = current_date - start_date

        if backfill_time.days < 90:
            return True
        return False

    @staticmethod
    def validate_format(date):
        """Validate Start date provided by user is in valid format.

        :param date: datetime
        :type date: str
        :return: True if the date is in valid format else False
        :rtype: boolean
        """
        try:
            res = bool(datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%f"))
        except ValueError as error:
            logger.error(error)
            res = False
        return res

    @staticmethod
    def check_observable_types(data):
        """Validate atleast one observable type is selected.

        :param date: datetime
        :type date: str
        :return: True if atleast one observable type selected else False
        :rtype: boolean
        """
        observable_types = [DOMAIN, EMAIL, PORT, IP, URI, FILEHASH, URL]
        is_selected = False
        for key, value in data.items():
            if key in observable_types and value == STR_ONE:
                is_selected = True

        return is_selected

    @staticmethod
    def validate_interval(interval):
        """Validate the interval is between 60s and 90 days.

        :param date: interval
        :type date: str
        :return: True if interval lies between min and max interval else False
        :rtype: boolean
        """
        if MIN_INTERVAL <= interval <= MAX_INTERVAL:
            logger.info(MIN_AND_MAX_INTERVAL)
            return True
        return False

    def validate(self, value, data):  # pylint: disable=W0613
        """
        Check if the url and api token provided by user is valid or not.

        :param value: value given in the Name field of configuration page/account.
        (Not required but only keeping as this method will be called with it by rest module.)
        :type value: str
        :param data: all the inputs provided by user in configuration page/account tab while saving.
        :type proxy: dict
        :return True or False
        """
        start_date = data[START_DATE]
        is_valid_format = ValidateInputs.validate_format(start_date)
        if not is_valid_format:
            logger.error(START_DATE_NOT_VALID_FORMAT)
            self.put_msg(START_DATE_NOT_VALID_FORMAT)
            return is_valid_format
        is_valid_backfill_days = ValidateInputs.check_start_date_days(start_date)
        if not is_valid_backfill_days:
            logger.info(BACKFILL_TIME_OLDER)
            self.put_msg(BACKFILL_TIME_OLDER)
            return is_valid_backfill_days

        is_selected = ValidateInputs.check_observable_types(data)

        if not is_selected:
            logger.info(SELECT_ATLEAST_ONE_OBSERVABLE_TYPE)
            self.put_msg(SELECT_ATLEAST_ONE_OBSERVABLE_TYPE_TO_BE_INGESTED)
            return is_selected

        is_valid_interval = ValidateInputs.validate_interval(data["interval"])
        if not is_valid_interval:
            logger.info(INTERVAL_MUST_BE_BETWEEN_MIN_AND_MAX_INTERVAL)
            self.put_msg(INTERVAL_MUST_BE_BETWEEN_MIN_AND_MAX_INTERVAL)
            return is_valid_interval

        return True
