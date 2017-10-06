from django.core.management.base import BaseCommand, CommandError
from stock_register.models import Stock
from user_login.models import Person


class Command(BaseCommand):
    """
    For extra documentation see: https://docs.djangoproject.com/en/1.8/howto/custom-management-commands/

    Execute this command: python manage.py set_initial_register_values
    """
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        jw = Person.objects.get(user_last_name="Bentum")
        jeroen = Person.objects.get(user_last_name="Jansen")

        for n in range(1, 18001):
            stock = Stock(owner=jw, stock_ref=str(n))
            stock.save()

        for n in range(18001, 20001):
            stock = Stock(owner=jeroen, stock_ref=str(n))
            stock.save()

            # create and put Stocks:
            #
            # Laurenss-MacBook-Pro-2:stockbroker laurens$ python manage.py shell
            # from stock_register.models import Stock
            # from user_login.models import Person
            # Person.objects.all()
            # jw = Person.objects.get(user_id=24)
            # >>>
            # Stock.objects.all()
            # Stock.objects.count()
