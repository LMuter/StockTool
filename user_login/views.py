import datetime
import re

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
# from django.core.mail import send_mail
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from django.utils.timezone import localtime, now

import models
import stock_order.controller as stock_order_controller
from bidding_round.bidding_round_manager import ExchangeManager
from bidding_round.models import BiddingRound
from constants import *
from models import Person, DuplicatePersonException, PasswordsException, UsernameException, PersonException
from stock_order.constants import *
from stock_order.order_manager import OrderManager
from stock_order.stock_order_helper import Period, constants_from_str
from stock_register.views import *
from user_login.models import UserLogin
from user_login.unicode_writer import UnicodeWriter
from email_conversation import email_manager
from email_conversation.models import EmailMessage
from email_conversation.email_manager import send_account_change_email


def get_ser_type(user_type):
    if user_type == STAFF:
        return 'employee'
    elif user_type == MODERATOR:
        return 'moderator'
    return 'third party'


def user_view(request):
    if request.user.is_authenticated():
        # person = Person.objects.get(user=request.user)
        # print request.user

        try:
            user_login = UserLogin.objects.get(user=request.user)
        except (UserLogin.DoesNotExist, ValueError):
            return redirect('home')

        person = user_login.person
        user = user_login.user

        order_manager = OrderManager()
        bidding_round_end = order_manager.get_bidding_round_end_date(person)
        bidding_round = order_manager.get_bidding_round(person)
        bidding_round_all = order_manager.get_all_bidding_rounds()

        user_stats = stock_order_controller.get_user_statistics(person)

        context = {'user_name': person.get_full_name(), 'user_type': get_ser_type(person.user_type),
                   'user_email': user.email, 'user_login_name': user.username, 'bidding_round_end': bidding_round_end,
                   'bidding_round_all': bidding_round_all, 'person': person, 'bidding_round': bidding_round,
                   'orders_placed_total': user_stats.get("orders_placed_total"),
                   'orders_placed_buy': user_stats.get("orders_placed_buy"),
                   'orders_placed_sell': user_stats.get("orders_placed_sell"),
                   'orders_placed_user': user_stats.get("orders_placed_user"),
                   'orders_placed_user_buy': user_stats.get("orders_placed_user_buy"),
                   'orders_placed_user_sell': user_stats.get("orders_placed_user_sell"),
                   'av_order_price_sell': user_stats.get("av_order_price_sell"),
                   'av_order_price_buy': user_stats.get("av_order_price_buy"),
                   'av_order_price_user_sell': user_stats.get("av_order_price_user_sell"),
                   'av_order_price_user_buy': user_stats.get("av_order_price_user_buy"),
                   'user_orders_left': user_stats.get("user_orders_left")}

        if person.user_type == MODERATOR:
            context["persons"] = Person.objects.all()

        if not context['user_name']:
            context['user_name'] = user_login.get_username()

        context["orders"] = order_manager.get_orders(person=person, order_status=PENDING_ACCEPTANCE)

        return render(request, 'user_login/user.html', context)
    return redirect('home')


def get_orders_view(request):
    """
    example: http://127.0.0.1:8000/orders/?&status=PENDING_ACCEPTANCE&user=T&timestamp=201512312359
    """
    # todo now it gets all orders from every active bidding round..
    context = {}

    status = request.GET.get('status', None)
    from_date = request.GET.get('timestamp', '')
    person = request.GET.get('user', None)
    period = None

    if request.user.is_authenticated():
        status = constants_from_str(status)

        if from_date:
            start_date = datetime.datetime.fromtimestamp(from_date)
            period = Period(start_date)

        if person == 'T':
            # person = Person.objects.get(user=request.user)
            user_login = UserLogin.objects.get(user=request.user)
            person = user_login.person

    try:
        manager = OrderManager()
        context["orders"] = manager.get_orders_as_dict(person=person, order_status=status, period=period)
    except Exception as e:
        context["error"] = e.message

    return HttpResponse(json.dumps(context), content_type="application/json")


def get_catalog_view(request):
    if request.user.is_authenticated():
        person = request.GET.get('user', None)
        compress = True
        if person == 'T':
            user_login = UserLogin.objects.get(user=request.user)
            person = user_login.person
        if compress and person is None:
            return get_stock_register_from_cache()
        return get_stock_register(person)
    return HttpResponseForbidden()


def index(request):
    if request.user.is_authenticated():
        return redirect('user')
    return login_user(request)


def register_view(request):
    if request.user.is_authenticated():
        return redirect('user')

    try:
        models.new_person(request.POST)
    except (DuplicatePersonException, PasswordsException, UsernameException) as e:
        context = {'message': e}
        return render(request, 'home/index.html', context)

    user = authenticate(username=request.POST.get('username'), password=request.POST.get('password'))

    try:
        login(request, user)
    except Exception as e:
        context = {'message': e}
        return render(request, 'home/index.html', context)

    return redirect('user')


def new_person_view(request):
    context = {}
    if request.user.is_authenticated():
        try:
            person = models.new_person_no_login(request.POST)
            context["message"] = "NAME: " + person.user_first_name + " " + person.user_last_name + ", E-MAIL: " + \
                                 person.user_email_address + ", ID: " + str(person.person_id) + " successfully created."
            context["person_id"] = person.person_id
            context["person_name"] = person.get_full_name()
        except DuplicatePersonException as e:
            context = {'error': e.message}
    return HttpResponse(json.dumps(context), content_type="application/json")


def new_login_view(request):
    context = {}
    if request.user.is_authenticated():
        try:
            new_login = models.new_person_login(request.POST)
            context["message"] = "NAME: " + new_login.user.username + ", E-MAIL: " + new_login.user.email + \
                                 " successfully created for " + new_login.person.get_full_name()
        except (PersonException, DuplicatePersonException, UsernameException, PasswordsException) as e:
            context = {'error': e.message}
    return HttpResponse(json.dumps(context), content_type="application/json")


def change_credentials_view(request):
    context = {}
    if request.user.is_authenticated():
        try:
            current_login = models.change_password(request.POST)
            context["message"] = "Password successfully updated for " + current_login.username
            conformation_email = request.POST.get('conformationMail')

            if conformation_email:
                send_account_change_email(date_time=localtime(now()), user_name=request.user.username,
                                          email_address=conformation_email, )


        except PasswordsException as e:
            context["error"] = e.message
    return HttpResponse(json.dumps(context), content_type="application/json")


def logout_view(request):
    logout(request)
    return redirect('index')


def new_order_view(request):
    context = {}
    if request.user.is_authenticated():
        person_id = request.POST.get("person")
        user_login = UserLogin.objects.get(user=request.user)
        person_login = user_login.person

        accept_terms = request.POST.get("terms") == 'on'
        is_definitive = False
        moderator = None

        if person_login.user_type == MODERATOR and person_id:
            if person_id == "empty":
                context["error"] = "No person is selected."
                return HttpResponse(json.dumps(context), content_type="application/json")

            accept_terms = True
            is_definitive = True
            moderator = person_login

            try:
                person = Person.objects.get(person_id=person_id)
            except Exception as e:
                context["error"] = e.message
                return HttpResponse(json.dumps(context), content_type="application/json")
        else:
            person = person_login

        amount = request.POST.get("amount").replace(",", ".")
        price = request.POST.get("price").replace(",", ".")

        order_type = UNDEFINED
        if request.POST.get("oder_type") == "buy":
            order_type = BUY
        elif request.POST.get("oder_type") == "sell":
            order_type = SELL

        try:
            manager = OrderManager()
            manager.create_order(person=person, amount=amount, price=price, order_type=order_type,
                                 accept_terms=accept_terms, status_definitive=is_definitive, moderator=moderator)
            context["message"] = "Order is placed."
            # email_manager.send_order_placed_email() #todo implement
        except Exception as e:
            context["error"] = e.message

    return HttpResponse(json.dumps(context), content_type="application/json")


def terms_view(request):
    return render(request, 'terms_and_conditions/index.html', {})


def login_user(request):
    username = request.POST.get('username')
    password = request.POST.get('password')

    if re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", username):

        try:
            raw_user = User.objects.get(email=username)
            username = raw_user.username
        except User.DoesNotExist:
            username = username
        except User.MultipleObjectsReturned:
            raw_user = User.objects.filter(email=username).first()
            username = raw_user.username

    user = authenticate(username=username, password=password)

    if user is not None:  # Return a 'disabled account' error message
        if user.is_active:  # Return an 'invalid login' error message.
            login(request, user)
            return redirect('user')

    context = {'message': 'Login failed.'}
    return render(request, 'home/index.html', context)


def test_transactions(request):
    context = {}
    exchange_manager = ExchangeManager()
    context["transactions"] = []
    transactions = exchange_manager.transactions_no_save()

    # todo move to stock_order.controller
    for trans in transactions:
        context["transactions"].append(
            [str(trans.id), unicode(trans.buy.owner.get_full_name()),
             unicode(trans.sell.owner.get_full_name()),
             str(trans.share_amount), str(trans.share_price), str(trans.share_amount * trans.share_price),
             str(timezone.localtime(trans.transaction_date))])

    return HttpResponse(json.dumps(context), content_type="application/json")


def export_transactions(request):
    """
    Create the HttpResponse object with the appropriate CSV header.
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="export_transactions.csv"'
    writer = UnicodeWriter(response)

    if request.user.is_authenticated():
        user_login = UserLogin.objects.get(user=request.user)
        person = user_login.person

        if person.user_type == MODERATOR:
            # todo remove logic to different place (helper or manager)
            writer.writerow(['This document is created on: ' + unicode(timezone.localtime(timezone.now()))])
            writer.writerow(['This document is created by: ' + unicode(person.get_full_name())])
            writer.writerow(
                ['id', 'buyer', 'seller', 'amount of shares', 'price per share', 'total price', 'transaction date'])

            round_id = request.GET.get('bidding_round_id', None)

            transactions = []

            if round_id:
                bidding_round = BiddingRound.objects.filter(round_id=round_id[0])
                exchange_manager = ExchangeManager()
                transactions = exchange_manager.get_transactions(bidding_rounds=bidding_round)

            # todo move to stock_order.controller
            for trans in transactions:
                writer.writerow(
                    [str(trans.id), unicode(trans.buy.owner.get_full_name()),
                     unicode(trans.sell.owner.get_full_name()),
                     str(trans.share_amount), str(trans.share_price), str(trans.share_amount * trans.share_price),
                     str(timezone.localtime(trans.transaction_date))])

        else:
            writer.writerow(["ERROR: moderator permission required for this action."])

        return response

    return HttpResponseForbidden()


def send_test_email(request):
    if request.user.is_authenticated():
        test_email = EmailMessage(
            from_email="info@careweb-certificaten.nl",
            to_emails=[request.user.email],
            subject="test",
            message="This is a test",
            sent_date=datetime.datetime.now(),
            email_user="email-user"
        )
        email_manager.send_email(test_email)
    return HttpResponseForbidden()


def export_stock_register(request):
    if request.user.is_authenticated():
        user_login = UserLogin.objects.get(user=request.user)
        person = user_login.person

        if person.user_type == MODERATOR:
            user_parameter = request.GET.get('user', None)
            if user_parameter == 'T':
                return get_stock_register_export(person=person, user_person=person)
            return get_stock_register_export(person=None, user_person=person)
    return HttpResponseForbidden()


def export_mailing_list(request):
    if request.user.is_authenticated():
        user_login = UserLogin.objects.get(user=request.user)
        person = user_login.person

        if person.user_type == MODERATOR:
            return get_mailing_list()
    return HttpResponseForbidden()
