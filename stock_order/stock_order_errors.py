__author__ = 'laurens'


class NoBiddingRoundException(Exception):
    pass


class BiddingRoundNotActiveException(Exception):
    pass


class UserTypeException(Exception):
    pass


class ExceedMaxOrderException(Exception):
    pass


class ExceedMaxSellSharesException(Exception):
    pass


class InvalidOrderTypeException(Exception):
    pass


class OrderPriceTypeException(Exception):
    pass


class OrderShareAmountException(Exception):
    pass


class OwnerNotFoundException(Exception):
    pass


class PlaceOrderException(Exception):
    pass


class OrderNotFoundException(Exception):
    pass


class OrderIsArchivedException(Exception):
    pass


class OrderCreationException(Exception):
    pass


class AlreadyAcceptedException(Exception):
    pass