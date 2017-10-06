__author__ = 'laurens'

from stock_order.models import StockOrder
from stock_order.constants import *


def get_total_sell_stock_amount(person):
    total_sell_stocks = 0

    try:
        sell_order_list = StockOrder.objects.all().filter(owner=person, order_type=SELL).exclude(is_archived=True)

        for order in sell_order_list:
            total_sell_stocks += order.order_amount_of_shares

    except StockOrder.DoesNotExist:
        return total_sell_stocks

    return total_sell_stocks


def constants_to_str(value):
    if value == BUY:
        return "BUY"
    elif value == SELL:
        return "SELL"
    elif value == UNDEFINED:
        return "UNDEFINED"
    else:
        return None


def constants_from_str(value):
    if value == 'undefined':
        return UNDEFINED
    elif value == 'BUY':
        return BUY
    elif value == 'SELL':
        return SELL
    elif value == "NEW":
        return NEW
    elif value == "PENDING_ACCEPTANCE":
        return PENDING_ACCEPTANCE
    elif value == "USER_ACCEPTED":
        return USER_ACCEPTED
    elif value == "DEFINITIVE":
        return DEFINITIVE
    elif value == "PROCESSED":
        return PROCESSED
    elif value == "WITHDRAWN":
        return WITHDRAWN
    else:
        return None


class Period():
    def __init__(self, start_date=None, end_date=None):
        self.start_date = start_date
        self.end_date = end_date

    def get_start_date(self):
        return self.start_date

    def get_end_date(self):
        return self.end_date