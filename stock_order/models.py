from django.db import models
from user_login.models import Person
from bidding_round.models import BiddingRound
from django.utils import timezone
from constants import *

#Run python manage.py makemigrations to create migrations for those changes.
#Run python manage.py check to check migrations for errors.
#Run python manage.py migrate to apply those changes to the database.


def create_stock_order(stock_order):
    return StockOrder.objects.get_or_create(encrypted_order_id=stock_order.encrypted_order_id,
                                            order_amount_of_shares=stock_order.order_amount_of_shares,
                                            order_price_per_share=stock_order.order_price_per_share,
                                            order_definite_number_of_shares=stock_order.order_definite_number_of_shares,
                                            order_definite_price=stock_order.order_definite_price,
                                            is_archived=stock_order.is_archived,
                                            owner=stock_order.owner,
                                            order_type=stock_order.order_type,
                                            order_result=stock_order.order_result,
                                            order_status=stock_order.order_status,
                                            bidding_round=stock_order.bidding_round,
    )[0]


def create_transaction(transaction):
    return Transaction.objects.create()


stock_order_readonly = ('order_id', 'order_result', 'order_definite_price',
                        'order_definite_number_of_shares', )


class StockOrder(models.Model):
    order_id = models.AutoField(primary_key=True)
    encrypted_order_id = models.CharField(max_length=50)

    order_amount_of_shares = models.IntegerField(default=0)
    order_price_per_share = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    order_definite_number_of_shares = models.IntegerField(default=0)
    order_definite_price = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    order_date = models.DateTimeField('order placed', default=timezone.now)

    is_archived = models.BooleanField(default=False)

    owner = models.ForeignKey(Person)

    bidding_round = models.ForeignKey(BiddingRound, default=0)

    # UNDEFINED | BUY | SELL
    order_type = models.CharField(max_length=2, choices=TYPE, default=UNDEFINED)

    # UNDEFINED | ASSIGNED_COMPLETE | ASSIGNED_PARTIAL | REJECTED
    order_result = models.CharField(max_length=2, choices=RESULT, default=UNDEFINED)

    # NEW | PENDING_ACCEPTANCE | USER_ACCEPTED | DEFINITIVE | PROCESSED | WITHDRAWN
    order_status = models.CharField(max_length=2, choices=STATUS, default=NEW)

    def __unicode__(self):
        return unicode("ID: " + str(self.order_id) + ', PRICE: ' + str(self.order_price_per_share) + ', AMOUNT: ' +
                       str(self.order_amount_of_shares) + ', STATUS: ' + str(self.order_status) + ' ' +
                       str(self.order_date))


class Transaction(models.Model):
    buy = models.ForeignKey(StockOrder, related_name='buy', default=-1, verbose_name="related order")
    sell = models.ForeignKey(StockOrder, related_name='sell', default=-1, verbose_name="related order")

    share_amount = models.IntegerField(default=0)
    share_price = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    # PROCESSED | REJECTED | UNDEFINED
    transaction_status = models.CharField(max_length=2, choices=TRANSACTION_STATUS, default=UNDEFINED)

    transaction_date = models.DateTimeField('transaction processed', default=timezone.now)

    def __unicode__(self):
        return unicode("SELL: " + str(self.sell.order_id) + ', BUY: ' + str(self.buy.order_id) + ', price: ' +
                       str(self.share_price) + ', amount: ' + str(self.share_amount))

