# coding=utf-8
from django.core.management.base import BaseCommand

from stock_register.models import Stock
from user_login.models import Person


class Command(BaseCommand):
    """
    For extra documentation see: https://docs.djangoproject.com/en/1.8/howto/custom-management-commands/

    Execute this command: python manage.py cert_update_okt_2016
    """

    def handle(self, *args, **options):
        jw = Person.objects.get(person_id=2)
        qruun = Person.objects.get(person_id=20)
        stephan = Person.objects.get(person_id=25)

        for n in range(20001, 39001):  # 19.000 cert for qruun
            stock = Stock(owner=qruun, stock_ref=str(n))
            stock.save()

            if n % 1000 == 0:
                print str(n) + " certificates created - Qruun"

        qruun.number_of_stocks = Stock.objects.filter(owner=qruun).count()
        qruun.save()

        print "[Done] Qruun (" + str(qruun.number_of_stocks) + " certificates in total for Qruun)"

        for n in range(39001, 64001):  # 25.000 cert for stephan
            stock = Stock(owner=stephan, stock_ref=str(n))
            stock.save()

            if n % 1000 == 0:
                print str(n) + " certificates created - Stephan"

        stephan.number_of_stocks = Stock.objects.filter(owner=stephan).count()
        stephan.save()

        print "[Done] Stephan (" + str(stephan.number_of_stocks) + " certificates in total for Stephan)"

        for n in range(64001, 200001):  # 136.000 cert for jw
            stock = Stock(owner=jw, stock_ref=str(n))
            stock.save()

            if n % 1000 == 0:
                print str(n) + " certificates created - JW"

        jw.number_of_stocks = Stock.objects.filter(owner=jw).count()
        jw.save()

        print "[Done] JW (" + str(jw.number_of_stocks) + " certificates in total for JW)"


"""
init:

>>> from stock_register.models import Stock
>>> from user_login.models import Person
>>> jw = Person.objects.get(person_id=3)
>>> qruun = Person.objects.get(person_id=5)
>>> stephan = Person.objects.get(person_id=6)


count:

>>> Stock.objects.filter(owner=jw).count()
152999
>>> Stock.objects.filter(owner=qruun).count()
20000
>>> Stock.objects.filter(owner=stephan).count()
25000


delete:

>>> Stock.objects.filter(owner=stephan).delete()
(25000, {u'stock_register.Stock': 25000, u'stock_register.Stock_transactions': 0})
>>> Stock.objects.filter(owner=qruun).delete()
(20000, {u'stock_register.Stock': 20000, u'stock_register.Stock_transactions': 0})
>>> Stock.objects.filter(owner=jw).delete()
(152999, {u'stock_register.Stock': 152999, u'stock_register.Stock_transactions': 0})
"""