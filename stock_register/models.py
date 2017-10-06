from django.db import models
from user_login.models import Person
from stock_order.models import Transaction
from stock_register.regiser_helper import random_str


class Stock(models.Model):
    stock_id = models.AutoField(primary_key=True)
    stock_ref = models.CharField(max_length=100, unique=True, default=random_str)
    owner = models.ForeignKey(Person)
    last_change = models.DateTimeField('last change', auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    transactions = models.ManyToManyField(Transaction)

    def __unicode__(self):
        return unicode("ID: " + unicode(self.stock_id) + ', OWNER: ' + unicode(self.owner) + ', LAST_CHANGE: ' +
                       unicode(self.last_change))


stock_readonly = ('stock_id', 'last_change', 'created', 'transactions')
