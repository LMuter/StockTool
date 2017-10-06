__author__ = 'laurens'

NEW = 'NE'
PENDING_ACCEPTANCE = 'AC'
USER_ACCEPTED = 'UA'
DEFINITIVE = 'DE'
PROCESSED = 'PR'
WITHDRAWN = 'WD'

UNDEFINED = 'UD'
BUY = 'BU'
SELL = 'SE'

ASSIGNED_COMPLETE = 'AC'
ASSIGNED_PARTIAL = 'AP'
REJECTED = 'RE'

STATUS = (
    (NEW, 'new'),
    (PENDING_ACCEPTANCE, 'pending for acceptance'),
    (USER_ACCEPTED, 'user has accepted'),
    (DEFINITIVE, 'definitive'),
    (PROCESSED, 'processed'),
    (WITHDRAWN, 'withdrawn'),
)

TYPE = (
    (UNDEFINED, 'undefined'),
    (BUY, 'buy'),
    (SELL, 'sell')
)

RESULT = (
    (UNDEFINED, 'undefined'),
    (ASSIGNED_COMPLETE, 'assigned complete'),
    (ASSIGNED_PARTIAL, 'assigned partial'),
    (REJECTED, 'rejected'),
)

TRANSACTION_STATUS = (
    (UNDEFINED, 'undefined'),
    (PROCESSED, 'processed'),
    (REJECTED, 'rejected'),
)