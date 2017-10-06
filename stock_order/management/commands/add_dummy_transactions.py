__author__ = 'laurens'


from stock_order.models import Transaction, StockOrder
from stock_order.constants import *
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    """
    For extra documentation see: https://docs.djangoproject.com/en/1.8/howto/custom-management-commands/
    """
    help = 'create 3 transactions'

    def handle(self, *args, **options):
        buy_orders = StockOrder.objects.filter(order_type=BUY)
        sell_orders = StockOrder.objects.filter(order_type=SELL)

        Transaction.objects.create(buy=buy_orders[0], sell=sell_orders[0], share_amount=3, share_price=12.5)
        Transaction.objects.create(buy=buy_orders[0], sell=sell_orders[0], share_amount=4, share_price=11.5)
        Transaction.objects.create(buy=buy_orders[0], sell=sell_orders[0], share_amount=5, share_price=10.5)