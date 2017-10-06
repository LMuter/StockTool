import json

from django.http import HttpResponse
from django.utils import timezone
from stock_register import controller
from user_login.unicode_writer import UnicodeWriter


def get_stock_register_from_cache():
    context = open(controller.get_register_cache_file_location())
    return HttpResponse(context, content_type="application/json")


def get_stock_register(person=None, compress=True):
    context = controller.get_stock_register_content(person, compress)
    return HttpResponse(json.dumps(context), content_type="application/json")


def get_stock_register_export(person=None, compress=True, user_person=None):
    if not user_person:
        raise Exception("No permission to write.")
    context = controller.get_stock_register_content(person, compress)
    return create_csv_file(context["register"], user_person)


def get_mailing_list():
    # todo mailing list download options:
    # - only certificate-holders, people with at least one certificate
    # - download entire mailing list
    response = get_csv_response("mailing_list.csv")
    writer = UnicodeWriter(response)
    mailing_list = controller.get_mailing_list()

    for mail_line in mailing_list:
        writer.writerow(mail_line)

    return response


def create_csv_file(context, user_person):
    headers = ['owner_id', 'owner_full_name', 'share_amount', 'share_ranges']
    response = get_csv_response("share_register_export.csv")
    writer = get_writer(user_person, headers, response)
    for item in context:
        writer_row = []
        for header_item in headers:
            writer_row.append(unicode(item.get(header_item, "")))
        writer.writerow(writer_row)
    return response


def get_writer(user_person, headers, response):
    writer = UnicodeWriter(response)
    writer.writerow(['This document is created on: ' + unicode(timezone.localtime(timezone.now()))])
    writer.writerow(['This document is created by: ' + unicode(user_person.get_full_name())])
    writer.writerow(headers)
    return writer


def get_csv_response(file_name="default.csv"):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="' + file_name + '"'
    return response
