from django.core.management.base import BaseCommand, CommandError
from stock_register.models import Stock


class Command(BaseCommand):
    """
    For extra documentation see: https://docs.djangoproject.com/en/1.8/howto/custom-management-commands/

    Execute this command: python manage.py delete_data
    """
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        Stock.objects.all().delete()
