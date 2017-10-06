__author__ = 'laurens'


THIRD_PARTY_ROUND = 'TR'
STAFF_ROUND = 'SR'
MODERATOR_ROUND = 'MR'
PROCESSED = 'PR'

BIDDING_ROUND_TYPE = (
    (THIRD_PARTY_ROUND, 'third party round'),
    (STAFF_ROUND, 'staff round'),
    (MODERATOR_ROUND, 'moderator round'),
    (PROCESSED, 'final'),
)


def get_number(key):
    return {
        THIRD_PARTY_ROUND: 0,
        STAFF_ROUND: 1,
        MODERATOR_ROUND: 2,
        PROCESSED: 3,
    }[key]