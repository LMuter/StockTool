__author__ = 'laurens'


class InvalidYearException(Exception):
    pass


class InvalidMonthException(Exception):
    pass


class InvalidValueException(Exception):
    pass


class OrderTypeException(Exception):
    pass


class BiddingRoundException(Exception):
    pass


class InactiveBiddingRoundException(Exception):
    pass


class SharePriceException(Exception):
    pass


class OrderStatusException(Exception):
    pass


class ShareAmountException(Exception):
    pass


class TransactionException(Exception):
    pass