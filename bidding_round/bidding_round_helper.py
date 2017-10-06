__author__ = 'laurens'

from django.utils import timezone
from datetime import timedelta, datetime
from home.date_time_constants import *
from bidding_round.bidding_round_errors import *


def get_start_date_third_party():
    return get_first_monday_of_month()


def get_end_date_third_party():
    delta = timedelta(days=5)
    return get_first_monday_of_month() + delta


def get_publication_date_third_party():
    delta = timedelta(days=7)
    return get_first_monday_of_month() + delta


def get_start_date_staff():
    delta = timedelta(days=7)
    return get_first_monday_of_month() + delta


def get_end_date_staff():
    delta = timedelta(days=12)
    return get_first_monday_of_month() + delta


def get_publication_date_staff():
    delta = timedelta(days=14)
    return get_first_monday_of_month() + delta


def get_start_date_moderator():
    delta = timedelta(days=14)
    return get_first_monday_of_month() + delta


def get_end_date_moderator():
    delta = timedelta(days=19)
    return get_first_monday_of_month() + delta


def get_publication_date_moderator():
    return get_first_monday_of_month(delta_month=1)


def get_handling_period_start():
    return get_first_monday_of_month(delta_month=1)


def get_handling_period_end():
    delta = timedelta(days=12)
    return get_first_monday_of_month(delta_month=1) + delta


def get_transaction_publication_date():
    delta = timedelta(days=14)
    return get_first_monday_of_month(delta_month=1) + delta


def get_first_monday_of_month(year=None, month=None, delta_year=0, delta_month=0):
    current_month = timezone.now().month
    current_year = timezone.now().year

    if not (year is None or (isinstance(year, int) and isinstance(delta_year, int))):
        raise InvalidValueException('Month or delta_month should be of type int.')

    if not (month is None or (isinstance(month, int) and isinstance(delta_month, int))):
        raise InvalidValueException('Year or delta_year should be of type int.')

    if year and month and (year < 2010 or year > 2038 or month < 1 or month > 12):
        raise InvalidValueException('Invalid year or month value, wrong range.')

    if year and year < current_year:
        raise InvalidYearException('Year may not be in the past.')

    if month and year == current_year and month <= current_month:
        raise InvalidMonthException('Month may not be in the past.')

    if not month:
        month = OCTOBER

    if not year:
        year = current_year

        if current_month >= month:
            year += 1

    return _get_weekday_first(year + delta_year, month + delta_month)


def _get_weekday_first(year, month):
    # get weekday of first day of the month

    if not (isinstance(year, int) and isinstance(month, int)):
        raise InvalidValueException('Year and month have to be of type int.')

    if year < 2010 or year > 2038 or month < 1 or month > 12:
        raise InvalidValueException('Invalid year or month value, wrong range.')

    dt = timezone.datetime(year=year, month=month, day=FIRST_DAY_OF_THE_MONTH).weekday()

    if dt == MONDAY:
        dt = FIRST_DAY_OF_THE_MONTH + SUNDAY

    day = WEEK_LEN - dt

    local_timezone = timezone.get_current_timezone()

    return datetime(year=year, month=month, day=day, tzinfo=local_timezone)