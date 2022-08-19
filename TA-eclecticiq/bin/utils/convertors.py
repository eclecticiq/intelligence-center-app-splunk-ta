"""Converters ."""

import datetime


def get_formatted_date(days):
    """Get Formatted datetime.

    :param days: backfill_time
    :type response: int
    :return: formatted date
    :rtype: str
    """
    time = datetime.datetime.now() - datetime.timedelta(days=days)
    return datetime.datetime.strftime(time, "%Y-%m-%dT%H:%M:%S.%f")


def get_current_time():
    """Get Current datetime.

    :return: current datetime
    :rtype: str
    """
    time = datetime.datetime.utcnow()
    return datetime.datetime.strftime(time, "%Y-%m-%dT%H:%M:%S.%f")


def format_time_to_iso(time):
    """Format time to ISO Format.

    :return: time
    :rtype: str
    """
    return datetime.datetime.strftime(time, "%Y-%m-%dT%H:%M:%S.%f")
