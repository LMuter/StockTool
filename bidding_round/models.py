from django.db import models
from constants import *
from bidding_round.bidding_round_helper import get_start_date_third_party, get_end_date_third_party, \
    get_publication_date_third_party, get_end_date_staff, get_start_date_staff, get_publication_date_staff, \
    get_start_date_moderator, get_end_date_moderator, get_publication_date_moderator, get_handling_period_start, \
    get_handling_period_end, get_transaction_publication_date


#Run python manage.py makemigrations to create migrations for those changes.
#Run python manage.py check to check migrations for errors.
#Run python manage.py migrate to apply those changes to the database.


class BiddingRound(models.Model):
    round_id = models.AutoField(primary_key=True)

    start_date_third_party = models.DateTimeField('start date third party', default=get_start_date_third_party)
    end_date_third_party = models.DateTimeField('end date third party', default=get_end_date_third_party)
    publication_date_third_party = models.DateTimeField('publication date third party',
                                                        default=get_publication_date_third_party)

    start_date_staff = models.DateTimeField('start date staff', default=get_start_date_staff)
    end_date_staff = models.DateTimeField('end date staff', default=get_end_date_staff)
    publication_date_staff = models.DateTimeField('publication date staff', default=get_publication_date_staff)

    start_date_moderator = models.DateTimeField('start date moderator', default=get_start_date_moderator)
    end_date_moderator = models.DateTimeField('end date moderator', default=get_end_date_moderator)
    publication_date_moderator = models.DateTimeField('publication date moderator',
                                                      default=get_publication_date_moderator)

    handling_period_start = models.DateTimeField('handling period start', default=get_handling_period_start)
    handling_period_end = models.DateTimeField('handling period end', default=get_handling_period_end)

    transaction_publication_date = models.DateTimeField('transaction publication date',
                                                        default=get_transaction_publication_date)

    is_active = models.BooleanField(default=False)

    # THIRD_PARTY_ROUND | STAFF_ROUND | MODERATOR_ROUND | HANDLING_PERIOD | PROCESSED
    round_type = models.CharField(max_length=2, choices=BIDDING_ROUND_TYPE, default=THIRD_PARTY_ROUND)

    total_shares_transferred = 0
    average_transaction_price = 0

    def __unicode__(self):
        return unicode(str(self.round_id) + ' ' + str(self.round_type))