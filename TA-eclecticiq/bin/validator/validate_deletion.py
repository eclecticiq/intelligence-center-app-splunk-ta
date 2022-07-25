"""Validate Inputs."""
import ta_eclecticiq_declare  # pylint: disable=W0611 # noqa: F401
import os
import splunk.admin as admin


from splunktaucclib.rest_handler.endpoint.validator import Validator
from validator.logger_manager import setup_logging

from constants.general import (
    MAX_INTERVAL,
    MIN_INTERVAL,
)

from constants.messages import (
    INTERVAL_MUST_BE_BETWEEN_MIN_AND_MAX_INTERVAL,
    MIN_AND_MAX_INTERVAL,
)


logger = setup_logging("ta_eclecticiq_validation_deletion")


class GetSessionKey(admin.MConfigHandler):  # type: ignore
    """Inheriting admin.MConfigHandler to get the current user's session key."""

    def __init__(self):
        """Set the session key as parameter to use while getting entities from Splunk REST."""
        self.session_key = self.getSessionKey()


class ValidateDeletion(Validator):  # type: ignore
    """Inheriting the Validator Class for creating custom validations."""

    def __init__(self, *args, **kwargs):  # pylint: disable=W0613
        """Create instance of ValidateAccount class along with Super class parameters Setting the my_app parameter as main TA directory name."""
        super().__init__()
        self.my_app = __file__.split(os.sep)[-4]

    @staticmethod
    def validate_min_max_numeric_value(interval):
        """Validate the interval is between 60s and 90 days.

        :param date: interval
        :type date: str
        :return: True if interval lies between min and max interval else False
        :rtype: boolean
        """
        if MIN_INTERVAL <= int(interval) <= MAX_INTERVAL:
            logger.info(MIN_AND_MAX_INTERVAL)
            return True
        return False

    @staticmethod
    def validate_min_max_numeric_observable_time(interval):
        """Validate the interval is between 60s and 90 days.

        :param date: interval
        :type date: str
        :return: True if interval lies between min and max interval else False
        :rtype: boolean
        """
        if 1 <= int(interval) <= 90:
            logger.info("Observable time to live is  between 1 day and 90 days ")
            return True
        return False

    @staticmethod
    def validate_integer_only(interval):
        """Validate the interval is between 60s and 90 days.

        :param date: interval
        :type date: str
        :return: True if interval lies between min and max interval else False
        :rtype: boolean
        """
        logger.info(interval)
        logger.info(type(interval))
        try:
            int(interval)
        except ValueError:
            logger.error("Time Interval is not an integer.")
            return False
        return True

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
        logger.info(data)
        observable_time_to_live = data["observable_time_to_live"]
        deletion_interval = data["interval"]
        is_numeric_interval = ValidateDeletion.validate_integer_only(deletion_interval)
        is_numeric_observable_time_to_live = ValidateDeletion.validate_integer_only(
            observable_time_to_live
        )
        if not is_numeric_interval:
            logger.info("Only Integer values are allowed for Interval !.")
            self.put_msg("Only Integer values are allowed Interval  !")
            return False

        if not is_numeric_observable_time_to_live:
            logger.info(
                "Only Integer values are allowed for Observable time to live !."
            )
            self.put_msg(
                "Only Integer values are allowed for Observable time to live  !"
            )
            return False

        is_valid_interval = ValidateDeletion.validate_min_max_numeric_value(
            deletion_interval
        )

        if not is_valid_interval:
            logger.info(INTERVAL_MUST_BE_BETWEEN_MIN_AND_MAX_INTERVAL)
            self.put_msg(INTERVAL_MUST_BE_BETWEEN_MIN_AND_MAX_INTERVAL)
            return False

        is_valid_observable_time = (
            ValidateDeletion.validate_min_max_numeric_observable_time(
                observable_time_to_live
            )
        )
        if not is_valid_observable_time:
            logger.info("Observable time to live must be  between 1 day and 90 days ")
            self.put_msg("Observable time to live must be between 1 day and 90 days ")
            return False

        return True
