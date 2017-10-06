import datetime

from django.db.models import Q
from django.utils import timezone
from django.utils.crypto import get_random_string

from bidding_round.constants import get_number as bidding_num
from bidding_round.models import BiddingRound
from email_conversation.email_manager import send_email
from email_conversation.models import EmailMessage
from stock_order import stock_order_helper as helper
from stock_order.constants import *
from stock_order.models import StockOrder, Transaction
from stock_order.models import create_stock_order
from stock_order.stock_order_errors import *
from stock_order.stock_order_helper import constants_to_str
from user_login.constants import *
from user_login.constants import get_number as person_num
from user_login.models import Person


# user places order -> order details are send -> user accepts order -> order is definitive -> definitive email is send
# all orders are processed -> order result is send -> order is archived


class OrderManager():
    def __init__(self):
        pass

    def get_orders(self, person=None, order_status=None, period=None, is_archived=False):
        """
        Returns all orders associated with given user
        optional period can be given as filter
        """
        if person:
            query = StockOrder.objects.filter(owner=person, is_archived=is_archived).order_by('order_date')
        else:
            query = StockOrder.objects.filter(Q(order_status=DEFINITIVE) | Q(order_status=PROCESSED) |
                                              Q(order_status=WITHDRAWN), is_archived=is_archived).order_by('order_date')

        if period:
            query = self._add_period_filter(query, period)

        if order_status:
            query = self._add_status_filter(query, order_status)

        return query

    def count_orders(self, person=None, order_status=None, period=None, order_type=None):
        query = self.get_orders(person=person, order_status=order_status, period=period)

        if order_type:
            query = query.filter(order_type=order_type)

        return query.count()

    def get_orders_as_dict(self, person=None, order_status=None, period=None):
        """
        return get_orders as dictionary
        """
        context = []
        orders = self.get_orders(person=person, order_status=order_status, period=period)

        for order in orders:
            order_as_dict = {"id": order.order_id, "type": constants_to_str(order.order_type),
                             "amount": int(order.order_amount_of_shares), "price": float(order.order_price_per_share),
                             "date": timezone.localtime(order.order_date).strftime("%-d %b '%y %-H:%M"),
                             "final_amount": "", "result": "", "final_price": "", "status": order.order_status,
                             "archived": bool(order.is_archived), "owner_username": order.owner.get_full_name(),
                             "owner_id": order.owner.person_id}

            if order.order_definite_number_of_shares:
                order_as_dict["final_amount"] = int(order.order_definite_number_of_shares)

            if order.order_definite_price:
                order_as_dict["final_price"] = float(order.order_definite_price)

            if order.order_result != UNDEFINED:
                if order.order_result == ASSIGNED_COMPLETE:
                    order_as_dict["result"] = "assigned complete"
                elif order.order_result == ASSIGNED_PARTIAL:
                    order_as_dict["result"] = "assigned partial"
                elif order.order_result == REJECTED:
                    order_as_dict["result"] = "rejected"

            context.append(order_as_dict)
        return context

    @staticmethod
    def _add_status_filter(query, order_status):
        return query.filter(order_status=order_status)

    @staticmethod
    def _add_period_filter(query, period):
        start_date = period.get_start_date
        end_date = period.get_end_date

        if start_date and end_date:
            return query.filter(order_date__gt=start_date, order_date__lt=end_date)
        elif start_date:
            return query.filter(order_date__gt=start_date, order_date__lt=datetime.date(2100, 1, 1))
        else:
            return query.filter(order_date__gt=datetime.date(1900, 1, 1), order_date__lt=end_date)

    def get_transactions(self, order, period=None):
        """
        Returns all transactions associated with given user
        optional period can be given as filter
        """
        if order.order_type == BUY:
            return self._get_buy_transactions(order, period)
        elif order.order_type == SELL:
            return self._get_sell_transactions(order, period)
        raise InvalidOrderTypeException("Order type should be SELL or BUY.")

    @staticmethod
    def _get_sell_transactions(sell_order, period):
        if period:
            start_date = period.get_start_date
            end_date = period.get_end_date

            if start_date and end_date:
                return Transaction.objects.filter(sell=sell_order, transaction_date__gt=start_date,
                                                  transaction_date__lt=end_date).order_by('transaction_date')
            elif start_date:
                return Transaction.objects.filter(sell=sell_order, transaction_date__gt=start_date,
                                                  transaction_date__lt=datetime.date(2100, 1, 1)).order_by(
                    'transaction_date')
            else:
                return Transaction.objects.filter(sell=sell_order, transaction_date__gt=datetime.date(1900, 1, 1),
                                                  transaction_date__lt=end_date).order_by('transaction_date')

        return Transaction.objects.get(sell=sell_order).order_by('transaction_date')

    @staticmethod
    def _get_buy_transactions(buy_order, period):
        if period:
            start_date = period.get_start_date
            end_date = period.get_end_date

            if start_date and end_date:
                return Transaction.objects.filter(buy=buy_order, transaction_date__gt=start_date,
                                                  transaction_date__lt=end_date).order_by('transaction_date')
            elif start_date:
                return Transaction.objects.filter(buy=buy_order, transaction_date__gt=start_date,
                                                  transaction_date__lt=datetime.date(2100, 1, 1)).order_by(
                    'transaction_date')
            else:
                return Transaction.objects.filter(buy=buy_order, transaction_date__gt=datetime.date(1900, 1, 1),
                                                  transaction_date__lt=end_date).order_by('transaction_date')

        return Transaction.objects.get(buy=buy_order).order_by('transaction_date')

    @staticmethod
    def can_place_order(person, stock_order, moderator_order=False):
        """
        checks if user can place order:
          * bidding period is active (first, second and third complete week of october)
              - first bidding round for third party and staff
              - second bidding round for staff
              - third bidding round for moderator
          * user has not exceeded his maximal bidding order number
          * total of non-archived SELL orders incl this one does not exceeded persons number_of_stocks (exp moderator_person)
        returns error message, None otherwise
        """
        try:
            bidding_round = stock_order.bidding_round
        except BiddingRound.DoesNotExist:
            raise NoBiddingRoundException('No bidding round active to place order.')

        if not bidding_round.is_active:
            raise BiddingRoundNotActiveException('Current bidding round is not active.')

        if moderator_order:
            if bidding_num(bidding_round.round_type) > MODERATOR:
                raise UserTypeException('User type does not match bidding round application.')
        else:
            if bidding_num(bidding_round.round_type) > person_num(person.user_type):
                raise UserTypeException('User type does not match bidding round application.')

        if person.number_of_orders_total >= person.number_of_orders_max:
            raise ExceedMaxOrderException('Placing this order would exceed max number of orders.')

        if stock_order.order_type == SELL:
            total_sell_stocks = helper.get_total_sell_stock_amount(person) + stock_order.order_amount_of_shares

            if person.number_of_stocks < total_sell_stocks:
                raise ExceedMaxSellSharesException('The number of SELL shares exceed users total number of shares.')
        return None

    @staticmethod
    def is_valid_order(stock_order):
        """
        checks if stock order is valid:
          * order must have a order_type BUY or SELL
          * order must have order_price_per_share (float)
          * order must have order_amount_of_shares (int)
          * order must have owner (Person)
        returns error message, None otherwise
        """
        if not (stock_order.order_type == SELL or stock_order.order_type == BUY):
            raise InvalidOrderTypeException('Type of order must be either SELL or BUY')

        if not (isinstance(stock_order.order_price_per_share, float) or
                    isinstance(stock_order.order_price_per_share, int)):
            raise OrderPriceTypeException('Price per share must be int or float.')

        if stock_order.order_price_per_share <= 0:
            raise OrderPriceTypeException('Price per share should not be zero or a negative number.')

        if not (isinstance(stock_order.order_amount_of_shares, int)):
            raise OrderShareAmountException('Amount of shares must be of type int.')

        if stock_order.order_amount_of_shares <= 0:
            raise OrderShareAmountException('Amount of shares should not be a negative number.')

        try:
            stock_order.owner
        except Person.DoesNotExist:
            raise OwnerNotFoundException('Owner of this order is missing or must be of type Person.')
        return None

    def place_order(self, stock_order, moderator_order=False, send_acceptance_mail=False):
        """
        checks if user can place order and if order is valid
        if so, save stock_order, update status to PENDING_ACCEPTANCE and update Person:
          * increase number_of_orders_total
          * increase number_of_orders_pending
          * call send_acceptance_email():
              - return any error message
        returns stock_order raise Exception if validation fails
        """
        try:
            self.is_valid_order(stock_order)
            person = stock_order.owner
            self.can_place_order(person, stock_order, moderator_order)
        except Exception as e:
            raise PlaceOrderException(e.message)

        person.number_of_orders_total += 1
        person.number_of_orders_pending += 1
        person.save()

        random_key = get_random_string(length=32)
        stock_order.encrypted_order_id = random_key
        stock_order = create_stock_order(stock_order)
        stock_order.save()

        if send_acceptance_mail:
            self._send_acceptance_email(random_key, stock_order)

        return stock_order

    def create_order(self, person, amount, price, order_type, accept_terms=False, bidding_round=None,
                     status_definitive=False, moderator=None):
        """
        create and places order
        """
        moderator_order = False

        if not accept_terms:
            raise OrderCreationException("Terms and conditions must be accepted.")

        if not bidding_round:
            if moderator:
                bidding_round = self.get_bidding_round(moderator)
                moderator_order = True
            else:
                bidding_round = self.get_bidding_round(person)

        if not bidding_round:
            raise OrderCreationException("No active bidding round found.")

        try:
            price = float(price)
        except ValueError:
            raise OrderCreationException("Invalid price value.")

        try:
            amount = int(float(amount))
        except ValueError:
            raise OrderCreationException("Invalid amount value.")

        stock_order = StockOrder()
        stock_order.owner = person
        stock_order.order_amount_of_shares = amount
        stock_order.order_price_per_share = price
        stock_order.order_type = order_type
        stock_order.bidding_round = bidding_round

        if status_definitive:
            stock_order.order_status = DEFINITIVE

        try:
            stock_order = self.place_order(stock_order, moderator_order)
        except Exception as e:
            raise OrderCreationException(e.message)

        return stock_order

    def get_bidding_round_end_date(self, person):
        bidding_round = self.get_bidding_round(person)

        if bidding_round:
            if person.user_type == THIRD_PARTY:
                return bidding_round.end_date_third_party
            elif person.user_type == STAFF:
                return bidding_round.end_date_staff
            elif person.user_type == MODERATOR:
                return bidding_round.end_date_moderator
        return None

    def get_order_total_value(self, person=None, order_status=None, order_type="SELL"):
        orders = self.get_orders_as_dict(person=person, order_status=order_status)

        price = 0
        for order in orders:
            if order.get("type") == order_type:
                price += order.get("amount") * order.get("price")
        return price

    def get_order_total_amount(self, person=None, order_status=None, order_type="SELL"):
        orders = self.get_orders_as_dict(person=person, order_status=order_status)

        amount = 0
        for order in orders:
            if order.get("type") == order_type:
                amount += order.get("amount")
        return amount

    def get_total_amount_and_price(self, person=None, order_status=None, order_type="SELL"):
        orders = self.get_orders_as_dict(person=person, order_status=order_status)

        amount = 0
        price = 0

        for order in orders:
            if order.get("type") == order_type:
                amount += order.get("amount", 0)
                price += order.get("price", 0)

        return amount, price

    @staticmethod
    def get_all_active_bidding_rounds():
        return BiddingRound.objects.filter(is_active=True)

    @staticmethod
    def get_all_bidding_rounds():
        return BiddingRound.objects.all()

    @staticmethod
    # todo write unit test..
    def get_bidding_round(person):
        now = timezone.now()

        if person.user_type == MODERATOR:
            moderator_query = BiddingRound.objects.filter(is_active=True, start_date_moderator__lte=now,
                                                          end_date_moderator__gt=now)
            if moderator_query.exists():
                return moderator_query.first()

        elif person.user_type == STAFF or person.user_type == MODERATOR:
            staff_query = BiddingRound.objects.filter(is_active=True, start_date_staff__lte=now, end_date_staff__gt=now)
            if staff_query.exists():
                return staff_query.first()

        if person.user_type == THIRD_PARTY or person.user_type == STAFF or person.user_type == MODERATOR:
            third_party_query = BiddingRound.objects.filter(is_active=True, start_date_third_party__lte=now,
                                                            end_date_third_party__gt=now)
            if third_party_query.exists():
                return third_party_query.first()

        return None

    def place_single_moderation_order(self, person, stock_order):
        """
        place_order() and update status to STAFF
        send acceptance_email to person and to moderator_person
        """
        self.place_order(stock_order)
        person.user_type = STAFF

    @staticmethod
    def _send_acceptance_email(random_key, stock_order):
        """
        generate random str for encrypted_order_id
        create message and send to user (user email_manager)
        returns error message, None otherwise
        """
        email = EmailMessage()
        email.to_emails = [stock_order.owner.user_email_address]
        name = stock_order.owner.get_full_name()
        email.from_email = 'laurens.muter@gmail.com'

        price_per_share = stock_order.order_price_per_share
        amount_of_shares = stock_order.order_amount_of_shares
        order_type = stock_order.order_type
        order_data = stock_order.order_date

        url = 'http://127.0.0.1:8000/user/' + random_key

        email.subject = 'Order definitief maken'

        email.message = "Beste " + name + ", \n\n" + \
                        "Hierbij ontvangt u een link waarmee u uw geplaatste order definitief kunt maken.\n\n" + \
                        "Order details: \n\nPrijs per aandeel: " + str(price_per_share) + "\n" + \
                        "Hoeveelheid certificaten: " + str(amount_of_shares) + "\n" + \
                        "Order type: " + str(order_type) + "\nOrder date: " + \
                        timezone.localtime(order_data).strftime("%-d %b '%y %-H:%M") + "\n\n" + url

        send_email(email)

        return None

    @staticmethod
    def accept_oder(person, encrypted_order_id):
        """
        find stock_order from encrypted_order_id and check:
          * status is PENDING_ACCEPTANCE
          * person is owner
          * stock_order not is_archived
        if so update stock_order:
          * order_status to USER_ACCEPTED
        and update person:
          * increase number_of_orders_accepted
          * decrease number_of_orders_pending
        returns error message, None otherwise
        """
        try:
            stock_order = StockOrder.objects.get(encrypted_order_id=encrypted_order_id, owner=person)
        except StockOrder.DoesNotExist:
            raise OrderNotFoundException('Given person does not have an order with given key.')

        if stock_order.is_archived:
            raise OrderIsArchivedException('Given order is archived.')

        if stock_order.order_status == USER_ACCEPTED:
            raise AlreadyAcceptedException('Given order is already accepted.')

        stock_order.order_status = USER_ACCEPTED
        stock_order.save()

        person.number_of_orders_accepted += 1
        person.number_of_orders_pending -= 1

        person.save()

        return None
