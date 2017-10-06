import json
from stock_register.constants import *
from stock_register.models import Stock
from stock_register.regiser_helper import *
from user_login.models import Person
from django.conf import settings


def list_stock_register_person(person=None):
    person_dict = {}

    if person:
        persons = [person]
    else:
        persons = Person.objects.all()

    for person in persons:
        person_stock_list = Stock.objects.filter(owner=person)
        person_dict[person] = []
        prev_stock = None

        if person_stock_list:
            for stock in person_stock_list:
                if not prev_stock:
                    person_dict[person].append([stock.stock_ref])

                elif int(stock.stock_ref) != int(prev_stock.stock_ref) + 1:
                    person_dict[person][-1].append(prev_stock.stock_ref)
                    person_dict[person].append([stock.stock_ref])

                prev_stock = stock

            person_dict[person][-1].append(person_stock_list[len(person_stock_list) - 1].stock_ref)

    return person_dict


def get_stock_register_content(person, compress=True):
    context = {"register": []}
    person_stock_dict = list_stock_register_person(person)
    persons = sorted(person_stock_dict.keys(), key=lambda x: (x.user_last_name, x.user_first_name))

    if compress:
        for person in persons:
            context["register"].append({"owner_id": str(person.person_id), "share_amount": str(person.number_of_stocks),
                                        "owner_full_name": person.get_full_name(),
                                        "share_ranges": person_stock_dict[person]})

        write_to_local_cache(context)

    # else:
    # todo implement complete stock register:
    # writer.writerow(['This document is created on: ' + unicode(timezone.localtime(timezone.now()))])
    # writer.writerow(['This document is created by: ' + unicode(person.get_full_name())])
    # writer.writerow(['id', 'reference', 'owner', 'last_change', 'created'])
    # stocks = Stock.objects.all()
    # for stock in stocks:
    #     writer.writerow(
    #         [str(stock.stock_id), unicode(stock.stock_ref), unicode(stock.owner.get_full_name()),
    #          str(timezone.localtime(stock.last_change)), str(timezone.localtime(stock.created))])

    return context


def write_to_local_cache(context):
    try:
        json_file = open(get_register_cache_file_location(), 'w')
        json_file.write(json.dumps(context))
    except:  # silent fail
        pass


def get_register_cache_file_location():
    # todo remove hardcoded dirs to settings
    if settings.DEBUG:
        return "/Users/laurens/Desktop/cache_register.json"
    return "/var/www/careweb-certificaten.nl/cache_register.json"


def get_compressed_stock_register_all():
    return get_stock_register_content(person=None, compress=True)


def get_mailing_list(include=(PERSON_STOCK_OWNER, PERSON_EMAIL_SUBSCRIBER)):
    persons = get_persons(include)
    email_list = []

    for person in persons:
        name_string = get_person_name_string(person)
        mail_string = "<" + person.user_email_address + ">"
        email_list.append([name_string + " " + mail_string])

    return email_list


def get_persons(*args):
    persons = Person.objects.all()
    if PERSON_STOCK_OWNER in args:
        persons = persons.filter(number_of_stocks_gt=0)
    return persons
