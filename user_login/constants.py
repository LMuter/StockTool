__author__ = 'laurens'

THIRD_PARTY = 'TP'
STAFF = 'ST'
MODERATOR = 'CA'


def get_number(key):
    return {
        THIRD_PARTY: 0,
        STAFF: 1,
        MODERATOR: 2,
    }[key]


USER_TYPES = (
    (THIRD_PARTY, 'third party'),
    (STAFF, 'staff'),
    (MODERATOR, 'moderator')
)

NO_EMAIL = "NE"
ON_STOCK_CHANGE = "SC"
ON_ACCOUNT_CHANGE = "AC"
ON_SALE_START = "SS"

USER_COMMUNICATION_TYPES = (
    (NO_EMAIL, 'no email'),
    (ON_STOCK_CHANGE, 'on stock change'),
    (ON_ACCOUNT_CHANGE, 'on account change'),
    (ON_SALE_START, 'on sale start')
)
