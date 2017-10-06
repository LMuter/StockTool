from django.shortcuts import render
from django.http import HttpResponse
from stock_register import controller
import json


# checks if user is logged in and linked to order from encrypted_order_id
# if user is not logged-in, show login field (user_name filled in)
# run order_manager.accept_oder, if it returns messages, show them
# else, render order accept page with order details and payment instructions
def accept_order_view(request):
    pass


def get_stock_register(person=None, comprime=True):
    context = {"transactions": controller.list_stock_register_person()}
    return HttpResponse(json.dumps(context), content_type="application/json")
