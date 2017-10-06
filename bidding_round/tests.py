from datetime import datetime

from django.test import TestCase
from django.utils import timezone

from bidding_round.bidding_round_errors import *
from bidding_round.bidding_round_manager import ExchangeManager, validate_transaction, OrderDict
from bidding_round.bidding_round_manager import StockOrderWrapper
from bidding_round.models import BiddingRound
from bidding_round_helper import _get_weekday_first, get_first_monday_of_month
from home.date_time_constants import *
from stock_order.constants import *
from stock_order.models import StockOrder
from stock_order.models import Transaction
from stock_order.order_manager import OrderManager
from stock_order.stock_order_errors import ExceedMaxSellSharesException
from user_login.models import new_person


class BiddingRoundHelperTestCase(TestCase):
    def setUp(self):
        self.current_year = timezone.now().year
        self.current_month = timezone.now().month

    def test_get_weekday_first(self):
        local_timezone = timezone.get_current_timezone()

        self.assertEquals(_get_weekday_first(year=2012, month=JANUARY),
                          datetime(year=2012, month=JANUARY, day=2, tzinfo=local_timezone))
        self.assertEquals(_get_weekday_first(year=2012, month=FEBRUARY),
                          datetime(year=2012, month=FEBRUARY, day=6, tzinfo=local_timezone))
        self.assertEquals(_get_weekday_first(year=2012, month=MARCH),
                          datetime(year=2012, month=MARCH, day=5, tzinfo=local_timezone))
        self.assertEquals(_get_weekday_first(year=2015, month=AUGUST),
                          datetime(year=2015, month=AUGUST, day=3, tzinfo=local_timezone))
        self.assertEquals(_get_weekday_first(year=2015, month=SEPTEMBER),
                          datetime(year=2015, month=SEPTEMBER, day=7, tzinfo=local_timezone))
        self.assertEquals(_get_weekday_first(year=2015, month=OCTOBER),
                          datetime(year=2015, month=OCTOBER, day=5, tzinfo=local_timezone))
        self.assertEquals(_get_weekday_first(year=2015, month=NOVEMBER),
                          datetime(year=2015, month=NOVEMBER, day=2, tzinfo=local_timezone))
        self.assertEquals(_get_weekday_first(year=2015, month=DECEMBER),
                          datetime(year=2015, month=DECEMBER, day=7, tzinfo=local_timezone))
        self.assertEquals(_get_weekday_first(year=2016, month=JANUARY),
                          datetime(year=2016, month=JANUARY, day=4, tzinfo=local_timezone))
        self.assertEquals(_get_weekday_first(year=2016, month=FEBRUARY),
                          datetime(year=2016, month=FEBRUARY, day=1, tzinfo=local_timezone))
        self.assertEquals(_get_weekday_first(year=2016, month=MARCH),
                          datetime(year=2016, month=MARCH, day=7, tzinfo=local_timezone))
        self.assertEquals(_get_weekday_first(year=2016, month=APRIL),
                          datetime(year=2016, month=APRIL, day=4, tzinfo=local_timezone))
        self.assertEquals(_get_weekday_first(year=2016, month=MAY),
                          datetime(year=2016, month=MAY, day=2, tzinfo=local_timezone))
        self.assertEquals(_get_weekday_first(year=2016, month=JUNE),
                          datetime(year=2016, month=JUNE, day=6, tzinfo=local_timezone))
        self.assertEquals(_get_weekday_first(year=2016, month=JULY),
                          datetime(year=2016, month=JULY, day=4, tzinfo=local_timezone))

    def test_get_first_monday_of_month(self):

        # =================================================================
        # test: current next year and this month, no errors expected
        # =================================================================

        month = self.current_month
        year = self.current_year + 1

        self.assertEquals(get_first_monday_of_month(year=year, month=month).weekday(), MONDAY)
        self.assertEquals(get_first_monday_of_month(year=None, month=month).weekday(), MONDAY)

        # =================================================================
        # test: Default month is october
        # =================================================================

        self.assertEquals(get_first_monday_of_month(year=year, month=None).weekday(), MONDAY)
        self.assertEquals(get_first_monday_of_month(year=None, month=None).weekday(), MONDAY)

        # =================================================================
        # test: InvalidYearException
        # =================================================================

        try:
            get_first_monday_of_month(year=self.current_year - 1, month=None)
            raise AssertionError('InvalidYearException expected')
        except InvalidYearException:
            pass

        # =================================================================
        # test: InvalidMonthException
        # =================================================================

        if self.current_month > 1:
            try:
                get_first_monday_of_month(year=self.current_year, month=self.current_month - 1)
                raise AssertionError('InvalidMonthException expected')
            except InvalidMonthException:
                pass

        # =================================================================
        # test: InvalidValueException
        # =================================================================

        try:
            get_first_monday_of_month(year="2015", month=None)
            raise AssertionError('InvalidValueException expected')
        except InvalidValueException:
            pass

        try:
            get_first_monday_of_month(year=None, month="10")
            raise AssertionError('InvalidValueException expected')
        except InvalidValueException:
            pass

        try:
            get_first_monday_of_month(year=2100, month=None)
            raise AssertionError('InvalidValueException expected')
        except InvalidValueException:
            pass

        try:
            get_first_monday_of_month(year=None, month=13)
            raise AssertionError('InvalidValueException expected')
        except InvalidValueException:
            pass

        try:
            get_first_monday_of_month(year=None, month=-1)
            raise AssertionError('InvalidValueException expected')
        except InvalidValueException:
            pass

        year = self.current_year

        if self.current_month > OCTOBER:
            year += 1

        self.assertEquals(get_first_monday_of_month(year=year, month=0).weekday(), MONDAY)


class BiddingRoundThirdPartyAndEmployerTestCase(TestCase):
    def setUp(self):
        self.order_manager = OrderManager()
        self.bidding_round_manager = ExchangeManager()

        self.third_party_0 = new_person(
            {'username': 'third_party_0', 'name': 'third_party_0', 'surname': 'third_party_0', 'password': 'test123',
             'passwordRetype': 'test123', 'email': 'third_party_0@test.nl'})

        self.third_party_1 = new_person(
            {'username': 'third_party_1', 'name': 'third_party_1', 'surname': 'third_party_1', 'password': 'test123',
             'passwordRetype': 'test123', 'email': 'third_party_1@test.nl'})

        self.third_party_2 = new_person(
            {'username': 'third_party_2', 'name': 'third_party_2', 'surname': 'third_party_2', 'password': 'test123',
             'passwordRetype': 'test123', 'email': 'third_party_2@test.nl'})

        self.employer_0 = new_person(
            {'username': 'employer_0', 'name': 'employer_0', 'surname': 'employer_0', 'password': 'test123',
             'passwordRetype': 'test123', 'email': 'employer_0@test.nl'})

        self.employer_1 = new_person(
            {'username': 'employer_1', 'name': 'employer_1', 'surname': 'employer_1', 'password': 'test123',
             'passwordRetype': 'test123', 'email': 'employer_1@test.nl'})

        self.employer_2 = new_person(
            {'username': 'employer_2', 'name': 'employer_2', 'surname': 'employer_2', 'password': 'test123',
             'passwordRetype': 'test123', 'email': 'employer_2@test.nl'})

        self.seller_0 = new_person(
            {'username': 'seller_0', 'name': 'seller_0', 'surname': 'seller_0', 'password': 'test123',
             'passwordRetype': 'test123', 'email': 'seller_0@test.nl'})

        self.seller_1 = new_person(
            {'username': 'seller_1', 'name': 'seller_1', 'surname': 'seller_1', 'password': 'test123',
             'passwordRetype': 'test123', 'email': 'seller_1@test.nl'})

        self.seller_0.number_of_stocks = 100
        self.seller_0.save()

        self.seller_1.number_of_stocks = 100
        self.seller_1.save()

        local_timezone = timezone.get_current_timezone()
        self.bidding_round = BiddingRound.objects.get_or_create(is_active=True)[0]
        self.bidding_round.start_date_third_party = datetime(year=2016, month=10, day=1, tzinfo=local_timezone)
        self.bidding_round.end_date_third_party = datetime(year=2016, month=10, day=3, tzinfo=local_timezone)
        self.bidding_round.start_date_staff = datetime(year=2016, month=10, day=4, tzinfo=local_timezone)
        self.bidding_round.end_date_staff = datetime(year=2016, month=10, day=6, tzinfo=local_timezone)
        self.bidding_round.start_date_moderator = datetime(year=2016, month=10, day=7, tzinfo=local_timezone)
        self.bidding_round.end_date_moderator = datetime(year=2016, month=10, day=9, tzinfo=local_timezone)
        self.bidding_round.save()

        stock_order_third_party_0 = StockOrder()
        stock_order_third_party_0.owner = self.third_party_0
        stock_order_third_party_0.order_type = BUY
        stock_order_third_party_0.order_amount_of_shares = 10
        stock_order_third_party_0.order_price_per_share = 20.00
        stock_order_third_party_0.bidding_round = self.bidding_round

        stock_order_third_party_1 = StockOrder()
        stock_order_third_party_1.owner = self.third_party_1
        stock_order_third_party_1.order_type = BUY
        stock_order_third_party_1.order_amount_of_shares = 10
        stock_order_third_party_1.order_price_per_share = 25.00
        stock_order_third_party_1.bidding_round = self.bidding_round

        stock_order_third_party_2 = StockOrder()
        stock_order_third_party_2.owner = self.third_party_2
        stock_order_third_party_2.order_type = BUY
        stock_order_third_party_2.order_amount_of_shares = 10
        stock_order_third_party_2.order_price_per_share = 30.00
        stock_order_third_party_2.bidding_round = self.bidding_round

        stock_order_employer_0 = StockOrder()
        stock_order_employer_0.owner = self.employer_0
        stock_order_employer_0.order_type = BUY
        stock_order_employer_0.order_amount_of_shares = 10
        stock_order_employer_0.order_price_per_share = 20.00
        stock_order_employer_0.bidding_round = self.bidding_round

        stock_order_employer_1 = StockOrder()
        stock_order_employer_1.owner = self.employer_1
        stock_order_employer_1.order_type = BUY
        stock_order_employer_1.order_amount_of_shares = 10
        stock_order_employer_1.order_price_per_share = 25.00
        stock_order_employer_1.bidding_round = self.bidding_round

        stock_order_employer_2 = StockOrder()
        stock_order_employer_2.owner = self.employer_2
        stock_order_employer_2.order_type = BUY
        stock_order_employer_2.order_amount_of_shares = 10
        stock_order_employer_2.order_price_per_share = 30.00
        stock_order_employer_2.bidding_round = self.bidding_round

        stock_order_seller_0 = StockOrder()
        stock_order_seller_0.owner = self.seller_0
        stock_order_seller_0.order_type = SELL
        stock_order_seller_0.order_amount_of_shares = 35
        stock_order_seller_0.order_price_per_share = 11.00
        stock_order_seller_0.bidding_round = self.bidding_round

        stock_order_seller_1 = StockOrder()
        stock_order_seller_1.owner = self.seller_1
        stock_order_seller_1.order_type = SELL
        stock_order_seller_1.order_amount_of_shares = 50
        stock_order_seller_1.order_price_per_share = 29.00
        stock_order_seller_1.bidding_round = self.bidding_round

        self.stock_order_third_party_0 = self.order_manager.place_order(stock_order_third_party_0)
        self.stock_order_third_party_1 = self.order_manager.place_order(stock_order_third_party_1)
        self.stock_order_third_party_2 = self.order_manager.place_order(stock_order_third_party_2)
        self.stock_order_employer_0 = self.order_manager.place_order(stock_order_employer_0)
        self.stock_order_employer_1 = self.order_manager.place_order(stock_order_employer_1)
        self.stock_order_employer_2 = self.order_manager.place_order(stock_order_employer_2)
        self.stock_order_seller_0 = self.order_manager.place_order(stock_order_seller_0)
        self.stock_order_seller_1 = self.order_manager.place_order(stock_order_seller_1)

        self.stock_order_third_party_0.order_date = datetime(year=2016, month=10, day=2, tzinfo=local_timezone)
        self.stock_order_third_party_1.order_date = datetime(year=2016, month=10, day=2, tzinfo=local_timezone)
        self.stock_order_third_party_2.order_date = datetime(year=2016, month=10, day=2, tzinfo=local_timezone)
        self.stock_order_employer_0.order_date = datetime(year=2016, month=10, day=5, tzinfo=local_timezone)
        self.stock_order_employer_1.order_date = datetime(year=2016, month=10, day=5, tzinfo=local_timezone)
        self.stock_order_employer_2.order_date = datetime(year=2016, month=10, day=5, tzinfo=local_timezone)
        self.stock_order_seller_0.order_date = datetime(year=2016, month=10, day=1, tzinfo=local_timezone)
        self.stock_order_seller_1.order_date = datetime(year=2016, month=10, day=1, tzinfo=local_timezone)

        self.stock_order_third_party_0.order_status = DEFINITIVE
        self.stock_order_third_party_1.order_status = DEFINITIVE
        self.stock_order_third_party_2.order_status = DEFINITIVE
        self.stock_order_employer_0.order_status = DEFINITIVE
        self.stock_order_employer_1.order_status = DEFINITIVE
        self.stock_order_employer_2.order_status = DEFINITIVE
        self.stock_order_seller_0.order_status = DEFINITIVE
        self.stock_order_seller_1.order_status = DEFINITIVE

        self.stock_order_third_party_0.save()
        self.stock_order_third_party_1.save()
        self.stock_order_third_party_2.save()
        self.stock_order_employer_0.save()
        self.stock_order_employer_1.save()
        self.stock_order_employer_2.save()
        self.stock_order_seller_0.save()
        self.stock_order_seller_1.save()

    def test_transactions_no_save(self):
        """
        * get all SELL orders with status DEFINITIVE and owner_type THIRD_PARTY, STAFF or MODERATOR
        * get all BUY orders with status DEFINITIVE and owner_type THIRD_PARTY, STAFF or MODERATOR
        * call transactions_no_save
        * all employers/moderation orders are handled first then left-overs are devided under third-party-orders
        * expected transactions:
            <Transaction: SELL: 7, BUY: 1, price: 11.00, amount: 2>
            <Transaction: SELL: 7, BUY: 2, price: 11.00, amount: 2>
            <Transaction: SELL: 7, BUY: 3, price: 11.00, amount: 1>
            <Transaction: SELL: 7, BUY: 4, price: 11.00, amount: 10>
            <Transaction: SELL: 7, BUY: 5, price: 11.00, amount: 10>
            <Transaction: SELL: 7, BUY: 6, price: 11.00, amount: 10>
            <Transaction: SELL: 8, BUY: 3, price: 29.00, amount: 9>
        """

        transactions = self.bidding_round_manager.transactions_no_save([self.bidding_round])
        transactions = sorted(transactions, key=lambda x: (x.sell.order_id, x.buy.order_id))
        transactions_iterator = iter(transactions)

        self.is_equal_transaction(transactions_iterator.next(),
                                  Transaction(sell=self.stock_order_seller_0, buy=self.stock_order_third_party_0,
                                              share_amount=2,
                                              share_price=self.stock_order_seller_0.order_price_per_share,
                                              transaction_status=PROCESSED))
        self.is_equal_transaction(transactions_iterator.next(),
                                  Transaction(sell=self.stock_order_seller_0, buy=self.stock_order_third_party_1,
                                              share_amount=2,
                                              share_price=self.stock_order_seller_0.order_price_per_share,
                                              transaction_status=PROCESSED))
        self.is_equal_transaction(transactions_iterator.next(),
                                  Transaction(sell=self.stock_order_seller_0, buy=self.stock_order_third_party_2,
                                              share_amount=1,
                                              share_price=self.stock_order_seller_0.order_price_per_share,
                                              transaction_status=PROCESSED))
        self.is_equal_transaction(transactions_iterator.next(),
                                  Transaction(sell=self.stock_order_seller_0, buy=self.stock_order_employer_0,
                                              share_amount=10,
                                              share_price=self.stock_order_seller_0.order_price_per_share,
                                              transaction_status=PROCESSED))
        self.is_equal_transaction(transactions_iterator.next(),
                                  Transaction(sell=self.stock_order_seller_0, buy=self.stock_order_employer_1,
                                              share_amount=10,
                                              share_price=self.stock_order_seller_0.order_price_per_share,
                                              transaction_status=PROCESSED))
        self.is_equal_transaction(transactions_iterator.next(),
                                  Transaction(sell=self.stock_order_seller_0, buy=self.stock_order_employer_2,
                                              share_amount=10,
                                              share_price=self.stock_order_seller_0.order_price_per_share,
                                              transaction_status=PROCESSED))
        self.is_equal_transaction(transactions_iterator.next(),
                                  Transaction(sell=self.stock_order_seller_1, buy=self.stock_order_third_party_2,
                                              share_amount=9,
                                              share_price=self.stock_order_seller_1.order_price_per_share,
                                              transaction_status=PROCESSED))

    def is_equal_transaction(self, real, expected):
        self.assertEquals(real.buy, expected.buy)
        self.assertEquals(real.sell, expected.sell)
        self.assertEquals(real.share_amount, expected.share_amount)
        self.assertEquals(real.share_price, expected.share_price)
        self.assertEquals(real.transaction_status, expected.transaction_status)


class BiddingRoundManagerTestCase(TestCase):
    def setUp(self):
        self.order_manager = OrderManager()
        self.bidding_round_manager = ExchangeManager()

        self.person_1 = new_person(
            {'username': 'testPerson1', 'name': 'Name1', 'surname': 'Surname1', 'password': 'test123',
             'passwordRetype': 'test123', 'email': 'test1@test.nl'})

        self.person_2 = new_person(
            {'username': 'testPerson2', 'name': 'Name2', 'surname': 'Surname2', 'password': 'test123',
             'passwordRetype': 'test123', 'email': 'test2@test.nl'})

        self.person_3 = new_person(
            {'username': 'testPerson3', 'name': 'Name3', 'surname': 'Surname3', 'password': 'test123',
             'passwordRetype': 'test123', 'email': 'test3@test.nl'})

        self.person_4 = new_person(
            {'username': 'testPerson4', 'name': 'Name4', 'surname': 'Surname4', 'password': 'test123',
             'passwordRetype': 'test123', 'email': 'test4@test.nl'})

        self.person_2.number_of_stocks = 100
        self.person_2.save()

        self.person_4.number_of_stocks = 100
        self.person_4.save()

        local_timezone = timezone.get_current_timezone()
        self.bidding_round = BiddingRound.objects.get_or_create(is_active=True)[0]
        self.bidding_round.start_date_moderator = datetime(year=datetime.now().year, month=datetime.now().month,
                                                           day=datetime.now().day - 1, tzinfo=local_timezone)
        self.bidding_round.end_date_moderator = datetime(year=datetime.now().year, month=datetime.now().month,
                                                         day=datetime.now().day + 1, tzinfo=local_timezone)
        self.bidding_round.save()

        stock_order_1 = StockOrder()
        stock_order_1.owner = self.person_1
        stock_order_1.order_type = BUY
        stock_order_1.order_amount_of_shares = 10
        stock_order_1.order_price_per_share = 6.00
        stock_order_1.bidding_round = self.bidding_round

        stock_order_2 = StockOrder()
        stock_order_2.owner = self.person_2
        stock_order_2.order_type = SELL
        stock_order_2.order_amount_of_shares = 10
        stock_order_2.order_price_per_share = 8.00
        stock_order_2.bidding_round = self.bidding_round

        stock_order_3 = StockOrder()
        stock_order_3.owner = self.person_1
        stock_order_3.order_type = BUY
        stock_order_3.order_amount_of_shares = 5
        stock_order_3.order_price_per_share = 8.00
        stock_order_3.bidding_round = self.bidding_round

        stock_order_4 = StockOrder()
        stock_order_4.owner = self.person_3
        stock_order_4.order_type = BUY
        stock_order_4.order_amount_of_shares = 10
        stock_order_4.order_price_per_share = 8.00
        stock_order_4.bidding_round = self.bidding_round

        stock_order_5 = StockOrder()
        stock_order_5.owner = self.person_2
        stock_order_5.order_type = SELL
        stock_order_5.order_amount_of_shares = 5
        stock_order_5.order_price_per_share = 10.00
        stock_order_5.bidding_round = self.bidding_round

        stock_order_6 = StockOrder()
        stock_order_6.owner = self.person_4
        stock_order_6.order_type = SELL
        stock_order_6.order_amount_of_shares = 5
        stock_order_6.order_price_per_share = 10.00
        stock_order_6.bidding_round = self.bidding_round

        stock_order_7 = StockOrder()
        stock_order_7.owner = self.person_1
        stock_order_7.order_type = BUY
        stock_order_7.order_amount_of_shares = 10
        stock_order_7.order_price_per_share = 10.00
        stock_order_7.bidding_round = self.bidding_round

        stock_order_8 = StockOrder()
        stock_order_8.owner = self.person_3
        stock_order_8.order_type = BUY
        stock_order_8.order_amount_of_shares = 10
        stock_order_8.order_price_per_share = 10.00
        stock_order_8.bidding_round = self.bidding_round

        stock_order_9 = StockOrder()
        stock_order_9.owner = self.person_2
        stock_order_9.order_type = SELL
        stock_order_9.order_amount_of_shares = 5
        stock_order_9.order_price_per_share = 12.00
        stock_order_9.bidding_round = self.bidding_round

        stock_order_10 = StockOrder()
        stock_order_10.owner = self.person_4
        stock_order_10.order_type = SELL
        stock_order_10.order_amount_of_shares = 5
        stock_order_10.order_price_per_share = 12.00
        stock_order_10.bidding_round = self.bidding_round

        stock_order_11 = StockOrder()
        stock_order_11.owner = self.person_3
        stock_order_11.order_type = BUY
        stock_order_11.order_amount_of_shares = 10
        stock_order_11.order_price_per_share = 12.00
        stock_order_11.bidding_round = self.bidding_round

        stock_order_12 = StockOrder()
        stock_order_12.owner = self.person_3
        stock_order_12.order_type = BUY
        stock_order_12.order_amount_of_shares = 5
        stock_order_12.order_price_per_share = 14.00

        stock_order_12.bidding_round = self.bidding_round

        stock_order_13 = StockOrder()
        stock_order_13.owner = self.person_4
        stock_order_13.order_type = SELL
        stock_order_13.order_amount_of_shares = 10
        stock_order_13.order_price_per_share = 16.00
        stock_order_13.bidding_round = self.bidding_round

        self.order_1 = self.order_manager.place_order(stock_order_1)
        self.order_2 = self.order_manager.place_order(stock_order_2)
        self.order_3 = self.order_manager.place_order(stock_order_3)
        self.order_4 = self.order_manager.place_order(stock_order_4)
        self.order_5 = self.order_manager.place_order(stock_order_5)
        self.order_6 = self.order_manager.place_order(stock_order_6)
        self.order_7 = self.order_manager.place_order(stock_order_7)
        self.order_8 = self.order_manager.place_order(stock_order_8)
        self.order_9 = self.order_manager.place_order(stock_order_9)
        self.order_10 = self.order_manager.place_order(stock_order_10)
        self.order_11 = self.order_manager.place_order(stock_order_11)
        self.order_12 = self.order_manager.place_order(stock_order_12)
        self.order_13 = self.order_manager.place_order(stock_order_13)

        self.order_1.order_status = DEFINITIVE
        self.order_2.order_status = DEFINITIVE
        self.order_3.order_status = DEFINITIVE
        self.order_4.order_status = DEFINITIVE
        self.order_5.order_status = DEFINITIVE
        self.order_6.order_status = DEFINITIVE
        self.order_7.order_status = DEFINITIVE
        self.order_8.order_status = DEFINITIVE
        self.order_9.order_status = DEFINITIVE
        self.order_10.order_status = DEFINITIVE
        self.order_11.order_status = DEFINITIVE
        self.order_12.order_status = DEFINITIVE
        self.order_13.order_status = DEFINITIVE

    def test_exchange_securities(self):
        """
        * create transaction_list
        * sort SELL-orders (lowest price first, then type MODERATOR first, final order_date)
        * securities exchange first round (BUY-order STAFF and MODERATOR):
            - call exchange_round
            - place returned transactions in transaction_list
        * securities exchange second round (BUY order THIRD_PARTY):
            - call exchange_round
            - merge returned transactions with transaction_list
        * update status of all shares to PROCESSED and order_result ASSIGNED_PARTIAL
        * return transaction_list
        """

        # =================================================================
        # test: one sell order and four buy orders
        #
        # expected transactions:
        #
        # SELL: 2, BUY: 3, price: 8.00, amount: 1
        # SELL: 2, BUY: 4, price: 8.00, amount: 2
        # SELL: 2, BUY: 7, price: 8.00, amount: 2
        # SELL: 2, BUY: 8, price: 8.00, amount: 2
        # SELL: 2, BUY: 11, price: 8.00, amount: 2
        # SELL: 2, BUY: 12, price: 8.00, amount: 1
        #
        # SELL: 5, BUY: 7, price: 10.00, amount: 2
        # SELL: 5, BUY: 8, price: 10.00, amount: 2
        # SELL: 5, BUY: 11, price: 10.00, amount: 1
        #
        # SELL: 6, BUY: 7, price: 10.00, amount: 1
        # SELL: 6, BUY: 8, price: 10.00, amount: 1
        # SELL: 6, BUY: 11, price: 10.00, amount: 2
        # SELL: 6, BUY: 12, price: 10.00, amount: 1
        #
        # SELL: 9, BUY: 11, price: 12.00, amount: 4
        #
        # SELL: 10, BUY: 11, price: 12.00, amount: 1
        # SELL: 10, BUY: 12, price: 12.00, amount: 3
        # =================================================================

        sell_orders = [StockOrderWrapper(self.order_2), StockOrderWrapper(self.order_5),
                       StockOrderWrapper(self.order_6), StockOrderWrapper(self.order_9),
                       StockOrderWrapper(self.order_10), StockOrderWrapper(self.order_13)]
        buy_orders = [StockOrderWrapper(self.order_1), StockOrderWrapper(self.order_3),
                      StockOrderWrapper(self.order_4), StockOrderWrapper(self.order_7),
                      StockOrderWrapper(self.order_8), StockOrderWrapper(self.order_11),
                      StockOrderWrapper(self.order_12)]

        transactions = self.bidding_round_manager.exchange_round(sell_orders=sell_orders, buy_orders=buy_orders)
        transactions = sorted(transactions, key=lambda x: (x.sell.order_id, x.buy.order_id))
        transactions_iterator = iter(transactions)

        trans_exp_buy_3_sell_2 = Transaction(buy=self.order_3, sell=self.order_2, share_amount=1,
                                             share_price=self.order_2.order_price_per_share,
                                             transaction_status=PROCESSED)
        trans_exp_buy_4_sell_2 = Transaction(buy=self.order_4, sell=self.order_2, share_amount=2,
                                             share_price=self.order_2.order_price_per_share,
                                             transaction_status=PROCESSED)
        trans_exp_buy_7_sell_2 = Transaction(buy=self.order_7, sell=self.order_2, share_amount=2,
                                             share_price=self.order_2.order_price_per_share,
                                             transaction_status=PROCESSED)
        trans_exp_buy_8_sell_2 = Transaction(buy=self.order_8, sell=self.order_2, share_amount=2,
                                             share_price=self.order_2.order_price_per_share,
                                             transaction_status=PROCESSED)
        trans_exp_buy_11_sell_2 = Transaction(buy=self.order_11, sell=self.order_2, share_amount=2,
                                              share_price=self.order_2.order_price_per_share,
                                              transaction_status=PROCESSED)
        trans_exp_buy_12_sell_2 = Transaction(buy=self.order_12, sell=self.order_2, share_amount=1,
                                              share_price=self.order_2.order_price_per_share,
                                              transaction_status=PROCESSED)

        trans_exp_buy_7_sell_5 = Transaction(buy=self.order_7, sell=self.order_5, share_amount=2,
                                             share_price=self.order_5.order_price_per_share,
                                             transaction_status=PROCESSED)
        trans_exp_buy_8_sell_5 = Transaction(buy=self.order_8, sell=self.order_5, share_amount=2,
                                             share_price=self.order_5.order_price_per_share,
                                             transaction_status=PROCESSED)
        trans_exp_buy_11_sell_5 = Transaction(buy=self.order_11, sell=self.order_5, share_amount=1,
                                              share_price=self.order_5.order_price_per_share,
                                              transaction_status=PROCESSED)

        trans_exp_buy_7_sell_6 = Transaction(buy=self.order_7, sell=self.order_6, share_amount=1,
                                             share_price=self.order_6.order_price_per_share,
                                             transaction_status=PROCESSED)
        trans_exp_buy_8_sell_6 = Transaction(buy=self.order_8, sell=self.order_6, share_amount=1,
                                             share_price=self.order_6.order_price_per_share,
                                             transaction_status=PROCESSED)
        trans_exp_buy_11_sell_6 = Transaction(buy=self.order_11, sell=self.order_6, share_amount=2,
                                              share_price=self.order_6.order_price_per_share,
                                              transaction_status=PROCESSED)
        trans_exp_buy_12_sell_6 = Transaction(buy=self.order_12, sell=self.order_6, share_amount=1,
                                              share_price=self.order_6.order_price_per_share,
                                              transaction_status=PROCESSED)

        trans_exp_buy_11_sell_9 = Transaction(buy=self.order_11, sell=self.order_9, share_amount=4,
                                              share_price=self.order_9.order_price_per_share,
                                              transaction_status=PROCESSED)

        trans_exp_buy_11_sell_10 = Transaction(buy=self.order_11, sell=self.order_10, share_amount=1,
                                               share_price=self.order_10.order_price_per_share,
                                               transaction_status=PROCESSED)
        trans_exp_buy_12_sell_10 = Transaction(buy=self.order_12, sell=self.order_10, share_amount=3,
                                               share_price=self.order_10.order_price_per_share,
                                               transaction_status=PROCESSED)

        self.is_equal_transaction(transactions_iterator.next(), trans_exp_buy_3_sell_2)
        self.is_equal_transaction(transactions_iterator.next(), trans_exp_buy_4_sell_2)
        self.is_equal_transaction(transactions_iterator.next(), trans_exp_buy_7_sell_2)
        self.is_equal_transaction(transactions_iterator.next(), trans_exp_buy_8_sell_2)
        self.is_equal_transaction(transactions_iterator.next(), trans_exp_buy_11_sell_2)
        self.is_equal_transaction(transactions_iterator.next(), trans_exp_buy_12_sell_2)

        self.is_equal_transaction(transactions_iterator.next(), trans_exp_buy_7_sell_5)
        self.is_equal_transaction(transactions_iterator.next(), trans_exp_buy_8_sell_5)
        self.is_equal_transaction(transactions_iterator.next(), trans_exp_buy_11_sell_5)

        self.is_equal_transaction(transactions_iterator.next(), trans_exp_buy_7_sell_6)
        self.is_equal_transaction(transactions_iterator.next(), trans_exp_buy_8_sell_6)
        self.is_equal_transaction(transactions_iterator.next(), trans_exp_buy_11_sell_6)
        self.is_equal_transaction(transactions_iterator.next(), trans_exp_buy_12_sell_6)

        self.is_equal_transaction(transactions_iterator.next(), trans_exp_buy_11_sell_9)

        self.is_equal_transaction(transactions_iterator.next(), trans_exp_buy_11_sell_10)
        self.is_equal_transaction(transactions_iterator.next(), trans_exp_buy_12_sell_10)

    def test_exchange_round(self):
        """
        * create transaction_list
        * sort BUY-orders (lowest price first)
        * BUY-order with price lower then lowest SELL order get order_result REJECTED
        * distribute shares:
            - SELL and BUY orders with status PROCESSED or WITHDRAWN are ignored
            - iterate over SELL-orders, per SELL order:
                o get all BUY-orders with price < SELL-order price, update status: PROCESSED, result: ASSIGNED_PARTIAL
                o get BUY-orders, higher/equal price (no status WITHDRAWN or PROCESSED), call share_distributor
                o merge returned transaction_list of share_distributor with transaction_list
        * return transaction_list
        """

        # =================================================================
        # test: one sell order and four buy orders
        #
        # expected calculation:
        #
        # order_5:   5
        # order_7:  10 -> 1.428571 -> 2
        # order_8:  10 -> 1.428571 -> 1
        # order_11: 10 -> 1.428571 -> 1
        # order_12: 5  -> 0.714286 -> 1
        # =================================================================

        sell_orders = [StockOrderWrapper(self.order_5)]
        buy_orders = [StockOrderWrapper(self.order_7), StockOrderWrapper(self.order_8),
                      StockOrderWrapper(self.order_11), StockOrderWrapper(self.order_12)]

        transactions = self.bidding_round_manager.exchange_round(sell_orders=sell_orders, buy_orders=buy_orders)
        transactions = sorted(transactions, key=lambda x: (x.sell.order_id, x.buy.order_id))
        transactions_iterator = iter(transactions)

        trans_exp_7 = Transaction(buy=self.order_7, sell=self.order_5, share_amount=2,
                                  share_price=self.order_5.order_price_per_share, transaction_status=PROCESSED)
        trans_exp_8 = Transaction(buy=self.order_8, sell=self.order_5, share_amount=1,
                                  share_price=self.order_5.order_price_per_share, transaction_status=PROCESSED)
        trans_exp_11 = Transaction(buy=self.order_11, sell=self.order_5, share_amount=1,
                                   share_price=self.order_5.order_price_per_share, transaction_status=PROCESSED)
        trans_exp_12 = Transaction(buy=self.order_12, sell=self.order_5, share_amount=1,
                                   share_price=self.order_5.order_price_per_share, transaction_status=PROCESSED)

        self.is_equal_transaction(transactions_iterator.next(), trans_exp_7)
        self.is_equal_transaction(transactions_iterator.next(), trans_exp_8)
        self.is_equal_transaction(transactions_iterator.next(), trans_exp_11)
        self.is_equal_transaction(transactions_iterator.next(), trans_exp_12)

        transactions = Transaction.objects.all()
        transactions.delete()

        # =================================================================
        # test: two sell orders (same price) and four buy orders
        #
        # expected calculation:
        #
        # order_5:   5
        # order_6:   5
        # order_7:  10 -> 2.85714286 -> 3
        # order_8:  10 -> 2.85714286 -> 3
        # order_11: 10 -> 2.85714286 -> 3
        # order_12: 5  -> 1.42857143 -> 1
        # =================================================================

        sell_orders = [StockOrderWrapper(self.order_5), StockOrderWrapper(self.order_6)]
        buy_orders = [StockOrderWrapper(self.order_7), StockOrderWrapper(self.order_8),
                      StockOrderWrapper(self.order_11), StockOrderWrapper(self.order_12)]

        transactions = self.bidding_round_manager.exchange_round(sell_orders=sell_orders, buy_orders=buy_orders)
        transactions = sorted(transactions, key=lambda x: (x.sell.order_id, x.buy.order_id))
        transactions_iterator = iter(transactions)

        trans_exp_buy_7_sell_5 = Transaction(buy=self.order_7, sell=self.order_5, share_amount=2,
                                             share_price=self.order_5.order_price_per_share,
                                             transaction_status=PROCESSED)
        trans_exp_buy_8_sell_5 = Transaction(buy=self.order_8, sell=self.order_5, share_amount=2,
                                             share_price=self.order_5.order_price_per_share,
                                             transaction_status=PROCESSED)
        trans_exp_buy_11_sell_5 = Transaction(buy=self.order_11, sell=self.order_5, share_amount=1,
                                              share_price=self.order_5.order_price_per_share,
                                              transaction_status=PROCESSED)

        trans_exp_buy_7_sell_6 = Transaction(buy=self.order_7, sell=self.order_6, share_amount=1,
                                             share_price=self.order_6.order_price_per_share,
                                             transaction_status=PROCESSED)
        trans_exp_buy_8_sell_6 = Transaction(buy=self.order_8, sell=self.order_6, share_amount=1,
                                             share_price=self.order_6.order_price_per_share,
                                             transaction_status=PROCESSED)
        trans_exp_buy_11_sell_6 = Transaction(buy=self.order_11, sell=self.order_6, share_amount=2,
                                              share_price=self.order_6.order_price_per_share,
                                              transaction_status=PROCESSED)
        trans_exp_buy_12_sell_6 = Transaction(buy=self.order_12, sell=self.order_6, share_amount=1,
                                              share_price=self.order_6.order_price_per_share,
                                              transaction_status=PROCESSED)

        self.is_equal_transaction(transactions_iterator.next(), trans_exp_buy_7_sell_5)
        self.is_equal_transaction(transactions_iterator.next(), trans_exp_buy_8_sell_5)
        self.is_equal_transaction(transactions_iterator.next(), trans_exp_buy_11_sell_5)

        self.is_equal_transaction(transactions_iterator.next(), trans_exp_buy_7_sell_6)
        self.is_equal_transaction(transactions_iterator.next(), trans_exp_buy_8_sell_6)
        self.is_equal_transaction(transactions_iterator.next(), trans_exp_buy_11_sell_6)
        self.is_equal_transaction(transactions_iterator.next(), trans_exp_buy_12_sell_6)

        transactions = Transaction.objects.all()
        transactions.delete()

        # =================================================================
        # test: four sell orders (multiple prices) and four buy orders
        #
        # expected calculation:
        #
        # order_5:   5
        # order_6:   5
        # order_7:  10 -> 2.85714286 -> 3
        # order_8:  10 -> 2.85714286 -> 3
        # order_11: 10 -> 2.85714286 -> 3 (shares left: 7)
        # order_12:  5 -> 1.42857143 -> 1 (shares left: 4)
        #
        # order_9:   5
        # order_10:  5
        # order_11:  7 -> 6.36363636 -> 6
        # order_12:  4 -> 3.63636363 -> 4
        # =================================================================

        sell_orders = [StockOrderWrapper(self.order_5), StockOrderWrapper(self.order_6),
                       StockOrderWrapper(self.order_9), StockOrderWrapper(self.order_10)]
        buy_orders = [StockOrderWrapper(self.order_7), StockOrderWrapper(self.order_8),
                      StockOrderWrapper(self.order_11), StockOrderWrapper(self.order_12)]

        transactions = self.bidding_round_manager.exchange_round(sell_orders=sell_orders, buy_orders=buy_orders)
        transactions = sorted(transactions, key=lambda x: (x.sell.order_id, x.buy.order_id))
        transactions_iterator = iter(transactions)

        trans_exp_buy_7_sell_5 = Transaction(buy=self.order_7, sell=self.order_5, share_amount=2,
                                             share_price=self.order_5.order_price_per_share,
                                             transaction_status=PROCESSED)
        trans_exp_buy_8_sell_5 = Transaction(buy=self.order_8, sell=self.order_5, share_amount=2,
                                             share_price=self.order_5.order_price_per_share,
                                             transaction_status=PROCESSED)
        trans_exp_buy_11_sell_5 = Transaction(buy=self.order_11, sell=self.order_5, share_amount=1,
                                              share_price=self.order_5.order_price_per_share,
                                              transaction_status=PROCESSED)

        trans_exp_buy_7_sell_6 = Transaction(buy=self.order_7, sell=self.order_6, share_amount=1,
                                             share_price=self.order_6.order_price_per_share,
                                             transaction_status=PROCESSED)
        trans_exp_buy_8_sell_6 = Transaction(buy=self.order_8, sell=self.order_6, share_amount=1,
                                             share_price=self.order_6.order_price_per_share,
                                             transaction_status=PROCESSED)
        trans_exp_buy_11_sell_6 = Transaction(buy=self.order_11, sell=self.order_6, share_amount=2,
                                              share_price=self.order_6.order_price_per_share,
                                              transaction_status=PROCESSED)
        trans_exp_buy_12_sell_6 = Transaction(buy=self.order_12, sell=self.order_6, share_amount=1,
                                              share_price=self.order_6.order_price_per_share,
                                              transaction_status=PROCESSED)

        trans_exp_buy_11_sell_9 = Transaction(buy=self.order_11, sell=self.order_9, share_amount=5,
                                              share_price=self.order_9.order_price_per_share,
                                              transaction_status=PROCESSED)

        trans_exp_buy_11_sell_10 = Transaction(buy=self.order_11, sell=self.order_10, share_amount=1,
                                               share_price=self.order_10.order_price_per_share,
                                               transaction_status=PROCESSED)
        trans_exp_buy_12_sell_10 = Transaction(buy=self.order_12, sell=self.order_10, share_amount=4,
                                               share_price=self.order_10.order_price_per_share,
                                               transaction_status=PROCESSED)

        self.is_equal_transaction(transactions_iterator.next(), trans_exp_buy_7_sell_5)
        self.is_equal_transaction(transactions_iterator.next(), trans_exp_buy_8_sell_5)
        self.is_equal_transaction(transactions_iterator.next(), trans_exp_buy_11_sell_5)

        self.is_equal_transaction(transactions_iterator.next(), trans_exp_buy_7_sell_6)
        self.is_equal_transaction(transactions_iterator.next(), trans_exp_buy_8_sell_6)
        self.is_equal_transaction(transactions_iterator.next(), trans_exp_buy_11_sell_6)
        self.is_equal_transaction(transactions_iterator.next(), trans_exp_buy_12_sell_6)

        self.is_equal_transaction(transactions_iterator.next(), trans_exp_buy_11_sell_9)

        self.is_equal_transaction(transactions_iterator.next(), trans_exp_buy_11_sell_10)
        self.is_equal_transaction(transactions_iterator.next(), trans_exp_buy_12_sell_10)

        transactions = Transaction.objects.all()
        transactions.delete()

        # =================================================================
        # test: more sell share amount then buy share amount
        #
        # expected calculation:
        #
        # order_2:  10 (sell order with price: 8.00 euro)
        # order_11: 10 -> 6.66666666 -> 7 (shares left: 3)
        # order_12:  5 -> 3.33333333 -> 3 (shares left: 2)
        #
        # because there more sell- then buy shares, distribution goes over sell-orders.
        #
        # order_11:  3 (buy order with price: 12.00 euro)
        # order_12:  2 (buy order with price: 14.00 euro)
        # order_5:   5 -> 2.5 -> 3 (sell price 10.00 euro)
        # order_6:   5 -> 2.5 -> 2 (sell price 10.00 euro)
        # =================================================================

        sell_orders = [StockOrderWrapper(self.order_2), StockOrderWrapper(self.order_5),
                       StockOrderWrapper(self.order_6)]
        buy_orders = [StockOrderWrapper(self.order_11), StockOrderWrapper(self.order_12)]

        transactions = self.bidding_round_manager.exchange_round(sell_orders=sell_orders, buy_orders=buy_orders)
        transactions = sorted(transactions, key=lambda x: (x.sell.order_id, x.buy.order_id))
        transactions_iterator = iter(transactions)

        trans_exp_buy_11_sell_2 = Transaction(buy=self.order_11, sell=self.order_2, share_amount=7,
                                              share_price=self.order_2.order_price_per_share,
                                              transaction_status=PROCESSED)
        trans_exp_buy_12_sell_2 = Transaction(buy=self.order_12, sell=self.order_2, share_amount=3,
                                              share_price=self.order_2.order_price_per_share,
                                              transaction_status=PROCESSED)

        trans_exp_buy_11_sell_5 = Transaction(buy=self.order_11, sell=self.order_5, share_amount=2,
                                              share_price=self.order_5.order_price_per_share,
                                              transaction_status=PROCESSED)
        trans_exp_buy_12_sell_5 = Transaction(buy=self.order_12, sell=self.order_5, share_amount=1,
                                              share_price=self.order_5.order_price_per_share,
                                              transaction_status=PROCESSED)

        trans_exp_buy_11_sell_6 = Transaction(buy=self.order_11, sell=self.order_6, share_amount=1,
                                              share_price=self.order_6.order_price_per_share,
                                              transaction_status=PROCESSED)
        trans_exp_buy_12_sell_6 = Transaction(buy=self.order_12, sell=self.order_6, share_amount=1,
                                              share_price=self.order_6.order_price_per_share,
                                              transaction_status=PROCESSED)

        self.is_equal_transaction(transactions_iterator.next(), trans_exp_buy_11_sell_2)
        self.is_equal_transaction(transactions_iterator.next(), trans_exp_buy_12_sell_2)

        self.is_equal_transaction(transactions_iterator.next(), trans_exp_buy_11_sell_5)
        self.is_equal_transaction(transactions_iterator.next(), trans_exp_buy_12_sell_5)

        self.is_equal_transaction(transactions_iterator.next(), trans_exp_buy_11_sell_6)
        self.is_equal_transaction(transactions_iterator.next(), trans_exp_buy_12_sell_6)

        transactions = Transaction.objects.all()
        transactions.delete()

        # =================================================================
        # test: excluded buy order, price to low
        # =================================================================

        sell_orders = [StockOrderWrapper(self.order_5)]
        buy_orders = [StockOrderWrapper(self.order_1), StockOrderWrapper(self.order_3), StockOrderWrapper(self.order_4),
                      StockOrderWrapper(self.order_7)]

        transactions = self.bidding_round_manager.exchange_round(sell_orders=sell_orders, buy_orders=buy_orders)

        self.assertEqual(len(transactions), 1)

        transactions = sorted(transactions, key=lambda x: (x.sell.order_id, x.buy.order_id))
        transactions_iterator = iter(transactions)

        trans_exp_buy_7_sell_5 = Transaction(buy=self.order_7, sell=self.order_5, share_amount=5,
                                             share_price=self.order_5.order_price_per_share,
                                             transaction_status=PROCESSED)

        self.is_equal_transaction(transactions_iterator.next(), trans_exp_buy_7_sell_5)

        # =================================================================
        # test: excluded sell order, price to high
        # =================================================================

        sell_orders = [StockOrderWrapper(self.order_6), StockOrderWrapper(self.order_9),
                       StockOrderWrapper(self.order_10), StockOrderWrapper(self.order_13)]
        buy_orders = [StockOrderWrapper(self.order_7)]

        transactions = self.bidding_round_manager.exchange_round(sell_orders=sell_orders, buy_orders=buy_orders)

        self.assertEqual(len(transactions), 1)

        transactions = sorted(transactions, key=lambda x: (x.sell.order_id, x.buy.order_id))
        transactions_iterator = iter(transactions)

        trans_exp_buy_7_sell_6 = Transaction(buy=self.order_7, sell=self.order_6, share_amount=5,
                                             share_price=self.order_6.order_price_per_share,
                                             transaction_status=PROCESSED)

        self.is_equal_transaction(transactions_iterator.next(), trans_exp_buy_7_sell_6)

    def test_share_distributor_float(self):

        # =================================================================
        # test: handled in share_distributor_float
        # =================================================================

        sell_orders = [StockOrderWrapper(self.order_5)]
        sell_5 = sell_orders[0]

        split_shares = 3.0

        buy_order_float_dict = OrderDict()

        buy_order_float_dict.add_order(key=.42857, order=StockOrderWrapper(self.order_7))
        buy_order_float_dict.add_order(key=.42857, order=StockOrderWrapper(self.order_8))
        buy_order_float_dict.add_order(key=.42857, order=StockOrderWrapper(self.order_11))
        buy_order_float_dict.add_order(key=.30429, order=StockOrderWrapper(self.order_12))

        result = self.bidding_round_manager.share_distributor_float(sell_orders, buy_order_float_dict, split_shares)

        result_dict = {}

        for res in result:
            result_dict[res.stock_order.order_id] = res

        order_real_7 = result_dict.get(7)
        order_real_8 = result_dict.get(8)
        order_real_11 = result_dict.get(11)
        order_real_12 = result_dict.get(12)

        sell_order_dict_1 = {sell_5: 1}

        order_exp_7 = StockOrderWrapper(self.order_7)
        order_exp_8 = StockOrderWrapper(self.order_8)
        order_exp_11 = StockOrderWrapper(self.order_11)
        order_exp_12 = StockOrderWrapper(self.order_12)

        order_exp_7.transaction_dict = sell_order_dict_1
        order_exp_8.transaction_dict = sell_order_dict_1
        order_exp_11.transaction_dict = sell_order_dict_1
        order_exp_12.transaction_dict = {}

        order_exp_7.shares_left = 9
        order_exp_8.shares_left = 9
        order_exp_11.shares_left = 9
        order_exp_12.shares_left = 5

        self.is_equal_order_wrapper(order_real_7, order_exp_7)
        self.is_equal_order_wrapper(order_real_8, order_exp_8)
        self.is_equal_order_wrapper(order_real_11, order_exp_11)
        self.is_equal_order_wrapper(order_real_12, order_exp_12)

        # =================================================================
        # test: handled in share_distributor_date
        # =================================================================

        sell_orders = [StockOrderWrapper(self.order_6)]
        sell_6 = sell_orders[0]

        split_shares = 2.0

        buy_order_float_dict = OrderDict()

        buy_order_float_dict.add_order(key=.42857, order=StockOrderWrapper(self.order_7))
        buy_order_float_dict.add_order(key=.42857, order=StockOrderWrapper(self.order_8))
        buy_order_float_dict.add_order(key=.42857, order=StockOrderWrapper(self.order_11))
        buy_order_float_dict.add_order(key=.30429, order=StockOrderWrapper(self.order_12))

        result = self.bidding_round_manager.share_distributor_float(sell_orders, buy_order_float_dict, split_shares)

        result_dict = {}

        for res in result:
            result_dict[res.stock_order.order_id] = res

        order_real_7 = result_dict.get(7)
        order_real_8 = result_dict.get(8)
        order_real_11 = result_dict.get(11)
        order_real_12 = result_dict.get(12)

        sell_order_dict_1 = {sell_6: 1}

        order_exp_7 = StockOrderWrapper(self.order_7)
        order_exp_8 = StockOrderWrapper(self.order_8)
        order_exp_11 = StockOrderWrapper(self.order_11)
        order_exp_12 = StockOrderWrapper(self.order_12)

        order_exp_7.transaction_dict = sell_order_dict_1
        order_exp_8.transaction_dict = sell_order_dict_1
        order_exp_11.transaction_dict = {}
        order_exp_12.transaction_dict = {}

        order_exp_7.shares_left = 9
        order_exp_8.shares_left = 9
        order_exp_11.shares_left = 10
        order_exp_12.shares_left = 5

        self.is_equal_order_wrapper(order_real_7, order_exp_7)
        self.is_equal_order_wrapper(order_real_8, order_exp_8)
        self.is_equal_order_wrapper(order_real_11, order_exp_11)
        self.is_equal_order_wrapper(order_real_12, order_exp_12)

        # =================================================================
        # test: handled in share_distributor_float and share_distributor_date
        # exp:
        #       - trans_real_3 is returned with no transactions
        #       - trans_real_4 is returned with no transactions
        #       - trans_real_7 is saved by share_distributor_date
        #       - trans_real_8 is saved by share_distributor_date
        #       - trans_real_11 is returned with no transactions
        #       - trans_real_12 is saved by share_distributor_float
        # =================================================================

        sell_orders = [StockOrderWrapper(self.order_2)]
        sell_2 = sell_orders[0]

        split_shares = 3.0

        buy_order_float_dict = OrderDict()

        buy_order_float_dict.add_order(key=.12857, order=StockOrderWrapper(self.order_3))
        buy_order_float_dict.add_order(key=.12857, order=StockOrderWrapper(self.order_4))
        buy_order_float_dict.add_order(key=.42857, order=StockOrderWrapper(self.order_7))
        buy_order_float_dict.add_order(key=.42857, order=StockOrderWrapper(self.order_8))
        buy_order_float_dict.add_order(key=.42857, order=StockOrderWrapper(self.order_11))
        buy_order_float_dict.add_order(key=.71429, order=StockOrderWrapper(self.order_12))

        result = self.bidding_round_manager.share_distributor_float(sell_orders, buy_order_float_dict, split_shares)

        result_dict = {}

        for res in result:
            result_dict[res.stock_order.order_id] = res

        order_real_3 = result_dict.get(3)
        order_real_4 = result_dict.get(4)
        order_real_7 = result_dict.get(7)
        order_real_8 = result_dict.get(8)
        order_real_11 = result_dict.get(11)
        order_real_12 = result_dict.get(12)

        sell_order_dict_1 = {sell_2: 1}

        order_exp_3 = StockOrderWrapper(self.order_3)
        order_exp_4 = StockOrderWrapper(self.order_4)
        order_exp_7 = StockOrderWrapper(self.order_7)
        order_exp_8 = StockOrderWrapper(self.order_8)
        order_exp_11 = StockOrderWrapper(self.order_11)
        order_exp_12 = StockOrderWrapper(self.order_12)

        order_exp_3.transaction_dict = {}
        order_exp_4.transaction_dict = {}
        order_exp_7.transaction_dict = sell_order_dict_1
        order_exp_8.transaction_dict = sell_order_dict_1
        order_exp_11.transaction_dict = {}
        order_exp_12.transaction_dict = sell_order_dict_1

        order_exp_3.shares_left = 5
        order_exp_4.shares_left = 10
        order_exp_7.shares_left = 9
        order_exp_8.shares_left = 9
        order_exp_11.shares_left = 10
        order_exp_12.shares_left = 4

        self.is_equal_order_wrapper(order_real_3, order_exp_3)
        self.is_equal_order_wrapper(order_real_4, order_exp_4)
        self.is_equal_order_wrapper(order_real_7, order_exp_7)
        self.is_equal_order_wrapper(order_real_8, order_exp_8)
        self.is_equal_order_wrapper(order_real_11, order_exp_11)
        self.is_equal_order_wrapper(order_real_12, order_exp_12)

    def test_share_distributor(self):
        """
        * create transaction_list
        * divide sell_order share_amount over buy_order in ratio of share_amount
        * round to whole shares, biggest decimal part first on equal use placement date
        * if shares are exchanged, call add_transaction per exchange
        * if shares_left of order is 0, set status to PROCESSED and order_result ASSIGNED_COMPLETE
        * call handle_transactions to complete all exchange
        * return list of non-completed orders
        """

        # =================================================================
        # test: complete test, share distribution int
        # =================================================================

        sell_list = [StockOrderWrapper(self.order_2)]
        sell = sell_list[0]
        buy_orders = [StockOrderWrapper(self.order_3), StockOrderWrapper(self.order_4), StockOrderWrapper(self.order_7),
                      StockOrderWrapper(self.order_8), StockOrderWrapper(self.order_11),
                      StockOrderWrapper(self.order_12)]

        result = self.bidding_round_manager.share_distributor(sell_orders=sell_list, buy_orders=buy_orders)

        order_real_3 = result[0]
        order_real_4 = result[1]
        order_real_7 = result[2]
        order_real_8 = result[3]
        order_real_11 = result[4]
        order_real_12 = result[5]

        sell_order_dict_1 = {sell: 1}
        sell_order_dict_2 = {sell: 2}

        order_exp_3 = StockOrderWrapper(self.order_3)
        order_exp_4 = StockOrderWrapper(self.order_4)
        order_exp_7 = StockOrderWrapper(self.order_7)
        order_exp_8 = StockOrderWrapper(self.order_8)
        order_exp_11 = StockOrderWrapper(self.order_11)
        order_exp_12 = StockOrderWrapper(self.order_12)

        order_exp_3.transaction_dict = sell_order_dict_1
        order_exp_4.transaction_dict = sell_order_dict_2
        order_exp_7.transaction_dict = sell_order_dict_2
        order_exp_8.transaction_dict = sell_order_dict_2
        order_exp_11.transaction_dict = sell_order_dict_2
        order_exp_12.transaction_dict = sell_order_dict_1

        order_exp_3.shares_left = 4
        order_exp_4.shares_left = 8
        order_exp_7.shares_left = 8
        order_exp_8.shares_left = 8
        order_exp_11.shares_left = 8
        order_exp_12.shares_left = 4

        self.is_equal_order_wrapper(order_real_3, order_exp_3)
        self.is_equal_order_wrapper(order_real_4, order_exp_4)
        self.is_equal_order_wrapper(order_real_7, order_exp_7)
        self.is_equal_order_wrapper(order_real_8, order_exp_8)
        self.is_equal_order_wrapper(order_real_11, order_exp_11)
        self.is_equal_order_wrapper(order_real_12, order_exp_12)

        # =================================================================
        # test: share distribution float easy
        # =================================================================

        sell_list = [StockOrderWrapper(self.order_2)]
        sell = sell_list[0]

        buy_order_3 = StockOrderWrapper(self.order_3)
        buy_order_4 = StockOrderWrapper(self.order_4)
        buy_order_7 = StockOrderWrapper(self.order_7)
        buy_order_8 = StockOrderWrapper(self.order_8)
        buy_order_11 = StockOrderWrapper(self.order_11)
        buy_order_12 = StockOrderWrapper(self.order_12)

        sell.shares_left = 6
        buy_order_3.shares_left = 8  # 2.4 -> 3
        buy_order_4.shares_left = 4  # 1.2 -> 1
        buy_order_7.shares_left = 4  # 1.2 -> 1
        buy_order_8.shares_left = 4  # 1.2 -> 1
        buy_order_11.shares_left = 0  # 0.0 -> 0
        buy_order_12.shares_left = 0  # 0.0 -> 0

        buy_orders = [buy_order_3, buy_order_4, buy_order_7, buy_order_8, buy_order_11, buy_order_12]

        result = self.bidding_round_manager.share_distributor(sell_orders=sell_list, buy_orders=buy_orders)

        result_dict = {}

        for res in result:
            result_dict[res.stock_order.order_id] = res

        try:
            # noinspection PyUnusedLocal
            dummy = result[4]
            raise AssertionError("IndexError exception expected")
        except IndexError:
            pass

        sell_order_dict_1 = {sell: 1}
        sell_order_dict_3 = {sell: 3}

        order_exp_3.transaction_dict = sell_order_dict_3
        order_exp_4.transaction_dict = sell_order_dict_1
        order_exp_7.transaction_dict = sell_order_dict_1
        order_exp_8.transaction_dict = sell_order_dict_1

        order_exp_3.shares_left = 5
        order_exp_4.shares_left = 3
        order_exp_7.shares_left = 3
        order_exp_8.shares_left = 3

        self.is_equal_order_wrapper(result_dict.get(3), order_exp_3)
        self.is_equal_order_wrapper(result_dict.get(4), order_exp_4)
        self.is_equal_order_wrapper(result_dict.get(7), order_exp_7)
        self.is_equal_order_wrapper(result_dict.get(8), order_exp_8)

        # =================================================================
        # test: share distribution float complex (multiple float iterations)
        # =================================================================

        sell_list = [StockOrderWrapper(self.order_2)]
        sell = sell_list[0]

        buy_order_3 = StockOrderWrapper(self.order_3)
        buy_order_4 = StockOrderWrapper(self.order_4)
        buy_order_7 = StockOrderWrapper(self.order_7)
        buy_order_8 = StockOrderWrapper(self.order_8)
        buy_order_11 = StockOrderWrapper(self.order_11)
        buy_order_12 = StockOrderWrapper(self.order_12)

        sell.shares_left = 18
        sell.stock_order.order_status = DEFINITIVE

        self.order_3.order_status = DEFINITIVE
        self.order_4.order_status = DEFINITIVE
        self.order_7.order_status = DEFINITIVE
        self.order_8.order_status = DEFINITIVE
        self.order_11.order_status = DEFINITIVE
        self.order_12.order_status = DEFINITIVE

        buy_order_3.shares_left = 6  # 3.6 -> 4
        buy_order_4.shares_left = 4  # 2.4 -> 2
        buy_order_7.shares_left = 2  # 1.2 -> 1
        buy_order_8.shares_left = 2  # 1.2 -> 1
        buy_order_11.shares_left = 8  # 4.8 -> 5
        buy_order_12.shares_left = 8  # 4.8 -> 5

        buy_orders = [buy_order_3, buy_order_4, buy_order_7, buy_order_8, buy_order_11, buy_order_12]

        result = self.bidding_round_manager.share_distributor(sell_orders=sell_list, buy_orders=buy_orders)

        result_dict = {}

        for res in result:
            result_dict[res.stock_order.order_id] = res

        try:
            # noinspection PyUnusedLocal
            dummy = result[6]
            raise AssertionError("IndexError exception expected")
        except IndexError:
            pass

        sell_order_dict_1 = {sell: 1}
        sell_order_dict_2 = {sell: 2}
        sell_order_dict_4 = {sell: 4}
        sell_order_dict_5 = {sell: 5}

        order_exp_3.transaction_dict = sell_order_dict_4
        order_exp_4.transaction_dict = sell_order_dict_2
        order_exp_7.transaction_dict = sell_order_dict_1
        order_exp_8.transaction_dict = sell_order_dict_1
        order_exp_11.transaction_dict = sell_order_dict_5
        order_exp_12.transaction_dict = sell_order_dict_5

        order_exp_3.shares_left = 2
        order_exp_4.shares_left = 2
        order_exp_7.shares_left = 1
        order_exp_8.shares_left = 1
        order_exp_11.shares_left = 3
        order_exp_12.shares_left = 3

        self.is_equal_order_wrapper(result_dict.get(3), order_exp_3)
        self.is_equal_order_wrapper(result_dict.get(4), order_exp_4)
        self.is_equal_order_wrapper(result_dict.get(7), order_exp_7)
        self.is_equal_order_wrapper(result_dict.get(8), order_exp_8)
        self.is_equal_order_wrapper(result_dict.get(11), order_exp_11)
        self.is_equal_order_wrapper(result_dict.get(12), order_exp_12)

        # =================================================================
        # test: share distribution date (two stocks left after one float iteration)
        # =================================================================

        sell_list = [StockOrderWrapper(self.order_2)]
        sell = sell_list[0]

        buy_order_3 = StockOrderWrapper(self.order_3)
        buy_order_4 = StockOrderWrapper(self.order_4)
        buy_order_7 = StockOrderWrapper(self.order_7)
        buy_order_8 = StockOrderWrapper(self.order_8)
        buy_order_11 = StockOrderWrapper(self.order_11)
        buy_order_12 = StockOrderWrapper(self.order_12)

        sell.shares_left = 19

        buy_order_3.shares_left = 4  # 2.4 -> 2 -> 3
        buy_order_4.shares_left = 4  # 2.4 -> 2 -> 3
        buy_order_7.shares_left = 4  # 2.4 -> 2 -> 2
        buy_order_8.shares_left = 2  # 1.2 -> 1 -> 1
        buy_order_11.shares_left = 8  # 4.8 -> 5 -> 5
        buy_order_12.shares_left = 8  # 4.8 -> 5 -> 5

        buy_orders = [buy_order_3, buy_order_4, buy_order_7, buy_order_8, buy_order_11, buy_order_12]

        result = self.bidding_round_manager.share_distributor(sell_orders=sell_list, buy_orders=buy_orders)

        result_dict = {}

        for res in result:
            result_dict[res.stock_order.order_id] = res

        try:
            # noinspection PyUnusedLocal
            dummy = result[6]
            raise AssertionError("IndexError exception expected")
        except IndexError:
            pass

        sell_order_dict_1 = {sell: 1}
        sell_order_dict_2 = {sell: 2}
        sell_order_dict_3 = {sell: 3}
        sell_order_dict_5 = {sell: 5}

        order_exp_3.transaction_dict = sell_order_dict_3
        order_exp_4.transaction_dict = sell_order_dict_3
        order_exp_7.transaction_dict = sell_order_dict_2
        order_exp_8.transaction_dict = sell_order_dict_1
        order_exp_11.transaction_dict = sell_order_dict_5
        order_exp_12.transaction_dict = sell_order_dict_5

        order_exp_3.shares_left = 1
        order_exp_4.shares_left = 1
        order_exp_7.shares_left = 2
        order_exp_8.shares_left = 1
        order_exp_11.shares_left = 3
        order_exp_12.shares_left = 3

        order_exp_11.order_status = DEFINITIVE
        order_exp_12.order_status = DEFINITIVE

        self.is_equal_order_wrapper(result_dict.get(3), order_exp_3)
        self.is_equal_order_wrapper(result_dict.get(4), order_exp_4)
        self.is_equal_order_wrapper(result_dict.get(7), order_exp_7)
        self.is_equal_order_wrapper(result_dict.get(8), order_exp_8)
        self.is_equal_order_wrapper(result_dict.get(11), order_exp_11)
        self.is_equal_order_wrapper(result_dict.get(12), order_exp_12)

        # =================================================================
        # test: share distribution int sell shares left
        # =================================================================

        sell_list = [StockOrderWrapper(self.order_2)]
        sell = sell_list[0]

        sell.shares_left = 100

        buy_order_3 = StockOrderWrapper(self.order_3)
        buy_order_4 = StockOrderWrapper(self.order_4)
        buy_order_7 = StockOrderWrapper(self.order_7)
        buy_order_8 = StockOrderWrapper(self.order_8)
        buy_order_11 = StockOrderWrapper(self.order_11)
        buy_order_12 = StockOrderWrapper(self.order_12)

        buy_order_3.shares_left = 4
        buy_order_4.shares_left = 7
        buy_order_7.shares_left = 9
        buy_order_8.shares_left = 4
        buy_order_11.shares_left = 8
        buy_order_12.shares_left = 3

        buy_orders = [buy_order_3, buy_order_4, buy_order_7, buy_order_8, buy_order_11, buy_order_12]

        result = self.bidding_round_manager.share_distributor(sell_orders=sell_list, buy_orders=buy_orders)

        order_exp_2 = StockOrderWrapper(self.order_2)
        order_exp_2.shares_left = 65

        self.is_equal_order_wrapper(result[0], order_exp_2)

        sell_order_dict_3 = {sell: 3}
        sell_order_dict_4 = {sell: 4}
        sell_order_dict_7 = {sell: 7}
        sell_order_dict_8 = {sell: 8}
        sell_order_dict_9 = {sell: 9}

        order_exp_3.transaction_dict = sell_order_dict_4
        order_exp_4.transaction_dict = sell_order_dict_7
        order_exp_7.transaction_dict = sell_order_dict_9
        order_exp_8.transaction_dict = sell_order_dict_4
        order_exp_11.transaction_dict = sell_order_dict_8
        order_exp_12.transaction_dict = sell_order_dict_3

        order_exp_3.shares_left = 0
        order_exp_4.shares_left = 0
        order_exp_7.shares_left = 0
        order_exp_8.shares_left = 0
        order_exp_11.shares_left = 0
        order_exp_12.shares_left = 0

        order_exp_3.order_status = PROCESSED
        order_exp_4.order_status = PROCESSED
        order_exp_7.order_status = PROCESSED
        order_exp_8.order_status = PROCESSED
        order_exp_11.order_status = PROCESSED
        order_exp_12.order_status = PROCESSED

        self.is_equal_order_wrapper(buy_order_3, order_exp_3)
        self.is_equal_order_wrapper(buy_order_4, order_exp_4)
        self.is_equal_order_wrapper(buy_order_7, order_exp_7)
        self.is_equal_order_wrapper(buy_order_8, order_exp_8)
        self.is_equal_order_wrapper(buy_order_11, order_exp_11)
        self.is_equal_order_wrapper(buy_order_12, order_exp_12)

    def test_validate_transaction(self):
        """
        * check if buy and sell order belong to same bidding_round-object
        * check if bidding round is active
        * check if buy-order-price-per-share is higher then sell-order-price-per-share
        * check if both buy and sell order have status DEFINITIVE
        * check if sell order has enough shares for transaction (share amount)
        * check if buy order has enough shares to buy for transaction (share amount)
        """
        sell = self.order_2
        buy = self.order_3
        amount = 5

        # =================================================================
        # test: BiddingRoundException
        # =================================================================

        different_bidding_round = BiddingRound.objects.create()
        sell.bidding_round = different_bidding_round

        try:
            validate_transaction(sell_order=sell, buy_order=buy, share_amount=amount)
            raise AssertionError('BiddingRoundException expected')
        except BiddingRoundException:
            pass

        sell.bidding_round = self.bidding_round
        buy.bidding_round = different_bidding_round

        try:
            validate_transaction(sell_order=sell, buy_order=buy, share_amount=amount)
            raise AssertionError('BiddingRoundException expected')
        except BiddingRoundException:
            pass

        buy.bidding_round = self.bidding_round

        # =================================================================
        # test: InactiveBiddingRoundException
        # =================================================================

        self.bidding_round.is_active = False

        try:
            validate_transaction(sell_order=sell, buy_order=buy, share_amount=amount)
            raise AssertionError('InactiveBiddingRoundException expected')
        except InactiveBiddingRoundException:
            pass

        self.bidding_round.is_active = True

        # =================================================================
        # test: OrderTypeException
        # =================================================================

        sell.order_type = BUY

        try:
            validate_transaction(sell_order=sell, buy_order=buy, share_amount=amount)
            raise AssertionError('OrderTypeException expected')
        except OrderTypeException:
            pass

        sell.order_type = SELL
        buy.order_type = SELL

        try:
            validate_transaction(sell_order=sell, buy_order=buy, share_amount=amount)
            raise AssertionError('OrderTypeException expected')
        except OrderTypeException:
            pass

        buy.order_type = BUY

        # =================================================================
        # test: SharePriceException
        # =================================================================

        sell.order_price_per_share = 9.0

        try:
            validate_transaction(sell_order=sell, buy_order=buy, share_amount=amount)
            raise AssertionError('SharePriceException expected')
        except SharePriceException:
            pass

        sell.order_price_per_share = 8.0
        buy.order_price_per_share = 7.0

        try:
            validate_transaction(sell_order=sell, buy_order=buy, share_amount=amount)
            raise AssertionError('SharePriceException expected')
        except SharePriceException:
            pass

        buy.order_price_per_share = 8.00

        # =================================================================
        # test: OrderStatusException
        # =================================================================

        sell.order_status = USER_ACCEPTED

        try:
            validate_transaction(sell_order=sell, buy_order=buy, share_amount=amount)
            raise AssertionError('OrderStatusException expected')
        except OrderStatusException:
            pass

        sell.order_status = DEFINITIVE
        buy.order_status = USER_ACCEPTED

        try:
            validate_transaction(sell_order=sell, buy_order=buy, share_amount=amount)
            raise AssertionError('OrderStatusException expected')
        except OrderStatusException:
            pass

        buy.order_status = DEFINITIVE

        # =================================================================
        # test: ShareAmountException
        # =================================================================

        sell.order_amount_of_shares = 4

        try:
            validate_transaction(sell_order=sell, buy_order=buy, share_amount=amount)
            raise AssertionError('ShareAmountException expected')
        except ShareAmountException:
            pass

        sell.order_amount_of_shares = 10
        buy.order_amount_of_shares = 4

        try:
            validate_transaction(sell_order=sell, buy_order=buy, share_amount=amount)
            raise AssertionError('ShareAmountException expected')
        except ShareAmountException:
            pass

    def test_bidding_round_handle_transactions(self):
        """
        * check if check_valid_persons_update is triggered
        """
        self.order_1.save()
        self.order_2.save()
        self.order_3.save()
        self.order_4.save()
        self.order_5.save()
        self.order_6.save()
        self.order_7.save()
        self.order_8.save()
        self.order_9.save()
        self.order_10.save()
        self.order_11.save()
        self.order_12.save()
        self.order_13.save()

        # =================================================================
        # test: sell order has more stocks then sell-person
        # =================================================================

        self.person_2.number_of_stocks = 0
        self.person_2.save()

        try:
            self.bidding_round_manager.handle_transactions(bidding_rounds=[self.bidding_round])
            raise AssertionError('ExceedMaxSellSharesException expected')
        except ExceedMaxSellSharesException:
            pass

    def is_equal_transaction(self, real, expected):
        self.assertEquals(real.buy, expected.buy)
        self.assertEquals(real.sell, expected.sell)
        self.assertEquals(real.share_amount, expected.share_amount)
        self.assertEquals(real.share_price, expected.share_price)
        self.assertEquals(real.transaction_status, expected.transaction_status)

    def is_equal_order_wrapper(self, real, expected):
        self.assertEquals(real.stock_order, expected.stock_order)
        self.assertEquals(real.order_status, expected.order_status)
        self.assertEquals(real.transaction_dict, expected.transaction_dict)
        self.assertEquals(real.shares_left, expected.shares_left)


class OrderDictTestCase(TestCase):
    def setUp(self):
        self.order_manager = OrderManager()
        self.bidding_round_manager = ExchangeManager()

        self.person_1 = new_person(
            {'username': 'testPerson1', 'name': 'Name1', 'surname': 'Surname1', 'password': 'test123',
             'passwordRetype': 'test123', 'email': 'test1@test.nl'})

        self.person_2 = new_person(
            {'username': 'testPerson2', 'name': 'Name2', 'surname': 'Surname2', 'password': 'test123',
             'passwordRetype': 'test123', 'email': 'test2@test.nl'})

        self.person_2.number_of_stocks = 100
        self.person_2.save()

        self.bidding_round = BiddingRound.objects.get_or_create(is_active=True)[0]

        stock_order_2 = StockOrder()
        stock_order_2.owner = self.person_2
        stock_order_2.order_type = SELL
        stock_order_2.order_amount_of_shares = 10
        stock_order_2.order_price_per_share = 8.00
        stock_order_2.bidding_round = self.bidding_round

        stock_order_3 = StockOrder()
        stock_order_3.owner = self.person_1
        stock_order_3.order_type = BUY
        stock_order_3.order_amount_of_shares = 5
        stock_order_3.order_price_per_share = 8.00
        stock_order_3.bidding_round = self.bidding_round

        stock_order_5 = StockOrder()
        stock_order_5.owner = self.person_2
        stock_order_5.order_type = SELL
        stock_order_5.order_amount_of_shares = 5
        stock_order_5.order_price_per_share = 10.00
        stock_order_5.bidding_round = self.bidding_round

        stock_order_7 = StockOrder()
        stock_order_7.owner = self.person_1
        stock_order_7.order_type = BUY
        stock_order_7.order_amount_of_shares = 10
        stock_order_7.order_price_per_share = 10.00
        stock_order_7.bidding_round = self.bidding_round

        self.order_2 = self.order_manager.place_order(stock_order_2)
        self.order_3 = self.order_manager.place_order(stock_order_3)
        self.order_5 = self.order_manager.place_order(stock_order_5)
        self.order_7 = self.order_manager.place_order(stock_order_7)

        self.order_2.order_status = DEFINITIVE
        self.order_3.order_status = DEFINITIVE
        self.order_5.order_status = DEFINITIVE
        self.order_7.order_status = DEFINITIVE

    def test_add_order(self):
        """
        - make key smaller then one
        - add key to dict, if entry does not exist, create entry
        """
        order_dict = OrderDict()

        order_dict.add_order(1.125, self.order_2)
        order_dict.add_order(10.321, self.order_3)
        order_dict.add_order(1.0, self.order_5)
        order_dict.add_order(.000123, self.order_7)

        dict_exp = {0.125: [self.order_2], 0.321: [self.order_3], 0.0: [self.order_5], .000123: [self.order_7]}

        # =================================================================
        # test: Correct key's and rounding of keys e.g. .321 and not 0.32099999999999973
        # =================================================================
        self.assertItemsEqual(dict_exp.keys(), order_dict.order_dict.keys())

        # =================================================================
        # test: Correct structure e.g. map order_2 to .125 etc.
        # =================================================================
        self.assertEquals(order_dict.order_dict, dict_exp)

    def test_get_max_key(self):
        order_dict = OrderDict()

        order_2 = StockOrderWrapper(self.order_2)
        order_3 = StockOrderWrapper(self.order_3)
        order_5 = StockOrderWrapper(self.order_5)
        order_7 = StockOrderWrapper(self.order_7)

        order_2.stock_order.order_status = DEFINITIVE
        order_3.stock_order.order_status = DEFINITIVE
        order_5.stock_order.order_status = DEFINITIVE
        order_7.stock_order.order_status = DEFINITIVE

        order_dict.add_order(1.125, order_2)
        order_dict.add_order(10.321, order_3)
        order_dict.add_order(1.4, order_5)
        order_dict.add_order(9.321, order_7)

        # =================================================================
        # test: max_key is created
        # =================================================================

        max_key = order_dict.get_max_key()
        self.assertEqual(max_key, 0.4)

        # =================================================================
        # test: max_key is updated after remove order
        # =================================================================

        order_dict.remove_max_key()

        max_key = order_dict.get_max_key()
        self.assertEqual(max_key, 0.321)

        # =================================================================
        # test: max_key is updated after remove entry
        # =================================================================

        # order_dict.remove_entry(key=.321)
        order_dict.remove_max_key()
        max_key = order_dict.get_max_key()
        self.assertEqual(max_key, 0.125)

    def test_get_max_key_entry(self):
        """
        return entry from max_key
        """
        order_dict = OrderDict()

        order_2 = StockOrderWrapper(self.order_2)
        order_3 = StockOrderWrapper(self.order_3)
        order_5 = StockOrderWrapper(self.order_5)
        order_7 = StockOrderWrapper(self.order_7)

        order_2.stock_order.order_status = DEFINITIVE
        order_3.stock_order.order_status = DEFINITIVE
        order_5.stock_order.order_status = DEFINITIVE
        order_7.stock_order.order_status = DEFINITIVE

        order_dict.add_order(1.125, order_2)
        order_dict.add_order(10.321, order_3)
        order_dict.add_order(1.4, order_5)
        order_dict.add_order(9.321, order_7)

        # =================================================================
        # test: max_key is created
        # =================================================================

        max_key_entry = order_dict.get_max_key_entry()
        exp_entry = [order_5]
        self.assertEqual(max_key_entry, exp_entry)

        # =================================================================
        # test: max_key is updated after remove order
        # =================================================================

        # order_dict.remove_order(key=.4, order=order_5)
        order_dict.remove_max_key()
        max_key_entry = order_dict.get_max_key_entry()
        exp_entry = [order_3, order_7]
        self.assertEqual(max_key_entry, exp_entry)

        # =================================================================
        # test: max_key is updated after remove entry
        # =================================================================

        # order_dict.remove_entry(key=.321)
        order_dict.remove_max_key()
        max_key_entry = order_dict.get_max_key_entry()
        exp_entry = [order_2]
        self.assertEqual(max_key_entry, exp_entry)

    def test_has_content(self):
        """
        return true if order_dict has at least one entry, false otherwise
        """
        order_dict = OrderDict()

        order_2 = StockOrderWrapper(self.order_2)
        order_3 = StockOrderWrapper(self.order_3)
        order_5 = StockOrderWrapper(self.order_5)
        order_7 = StockOrderWrapper(self.order_7)

        order_2.stock_order.order_status = DEFINITIVE
        order_3.stock_order.order_status = DEFINITIVE
        order_5.stock_order.order_status = DEFINITIVE
        order_7.stock_order.order_status = DEFINITIVE

        order_dict.add_order(1.125, order_2)
        order_dict.add_order(10.321, order_3)
        order_dict.add_order(1.4, order_5)
        order_dict.add_order(9.321, order_7)

        self.assertTrue(order_dict.has_content())

        # =================================================================
        # test: remove order, dict has still content
        # =================================================================

        # order_dict.remove_order(key=.4, order=order_5)
        del (order_dict.order_dict[.4])
        self.assertTrue(order_dict.has_content())

        # =================================================================
        # test: remove entry, dict has still content
        # =================================================================

        # order_dict.remove_entry(key=.321)
        del (order_dict.order_dict[.321])
        self.assertTrue(order_dict.has_content())

        # =================================================================
        # test: remove last order, dict has no content
        # =================================================================

        # order_dict.remove_order(key=.125, order=order_2)
        del (order_dict.order_dict[.125])
        self.assertFalse(order_dict.has_content())

    def test_reset_values(self):
        """
        reset all values
        """
        order_dict = OrderDict()

        order_2 = StockOrderWrapper(self.order_2)
        order_3 = StockOrderWrapper(self.order_3)
        order_5 = StockOrderWrapper(self.order_5)
        order_7 = StockOrderWrapper(self.order_7)

        order_2.stock_order.order_status = DEFINITIVE
        order_3.stock_order.order_status = DEFINITIVE
        order_5.stock_order.order_status = DEFINITIVE
        order_7.stock_order.order_status = DEFINITIVE

        order_dict.add_order(1.125, order_2)
        order_dict.add_order(10.321, order_3)
        order_dict.add_order(1.4, order_5)
        order_dict.add_order(9.321, order_7)

        # =================================================================
        # test: values reset
        # =================================================================

        order_dict.order_dict = {}
        order_dict.max_key = 0

        self.assertEqual(order_dict.order_dict, {})
        self.assertEqual(order_dict.max_key, 0)
        self.assertIsNone(order_dict.get_max_key_entry())
        self.assertFalse(order_dict.has_content())

    def test_flatten_dict(self):
        """
        - place all orders from order_dict in list
        - skip processed orders
        """
        order_dict = OrderDict()

        order_2 = StockOrderWrapper(self.order_2)
        order_3 = StockOrderWrapper(self.order_3)
        order_5 = StockOrderWrapper(self.order_5)
        order_7 = StockOrderWrapper(self.order_7)

        order_2.stock_order.order_status = DEFINITIVE
        order_3.stock_order.order_status = DEFINITIVE
        order_5.stock_order.order_status = DEFINITIVE
        order_7.stock_order.order_status = DEFINITIVE

        order_dict.add_order(1.125, order_2)
        order_dict.add_order(10.321, order_3)
        order_dict.add_order(1.4, order_5)
        order_dict.add_order(9.321, order_7)

        # =================================================================
        # test: flattened dict contains all orders
        # =================================================================

        order_list = order_dict.flatten_dict()
        exp_list = [order_2, order_3, order_5, order_7]
        self.assertItemsEqual(exp_list, order_list)

        # =================================================================
        # test: exclude keys
        # =================================================================

        exclude_list = [.125, .4]
        order_list = order_dict.flatten_dict(exclude_keys=exclude_list)
        exp_list = [order_3, order_7]
        self.assertItemsEqual(exp_list, order_list)

        exclude_list = [0.125, 0.4]
        order_list = order_dict.flatten_dict(exclude_keys=exclude_list)
        exp_list = [order_3, order_7]
        self.assertItemsEqual(exp_list, order_list)

        # =================================================================
        # test: exclude non-existing key
        # =================================================================

        exclude_list = [.543, .9753]
        order_list = order_dict.flatten_dict(exclude_keys=exclude_list)
        exp_list = [order_2, order_3, order_5, order_7]
        self.assertItemsEqual(exp_list, order_list)

        exclude_list = [1, 4]
        order_list = order_dict.flatten_dict(exclude_keys=exclude_list)
        exp_list = [order_2, order_3, order_5, order_7]
        self.assertItemsEqual(exp_list, order_list)

        exclude_list = [".125", ".4"]
        order_list = order_dict.flatten_dict(exclude_keys=exclude_list)
        exp_list = [order_2, order_3, order_5, order_7]
        self.assertItemsEqual(exp_list, order_list)

    def is_equal_transaction(self, real, expected):
        self.assertEquals(real.buy, expected.buy)
        self.assertEquals(real.sell, expected.sell)
        self.assertEquals(real.share_amount, expected.share_amount)
        self.assertEquals(real.share_price, expected.share_price)
        self.assertEquals(real.transaction_status, expected.transaction_status)

    def is_equal_order_wrapper(self, real, expected):
        self.assertEquals(real.stock_order, expected.stock_order)
        self.assertEquals(real.order_status, expected.order_status)
        self.assertEquals(real.transaction_dict, expected.transaction_dict)


class StockOrderWrapperTestCase(TestCase):
    def setUp(self):
        self.order_manager = OrderManager()
        self.bidding_round_manager = ExchangeManager()

        self.person_1 = new_person(
            {'username': 'testPerson1', 'name': 'Name1', 'surname': 'Surname1', 'password': 'test123',
             'passwordRetype': 'test123', 'email': 'test1@test.nl'})

        self.person_2 = new_person(
            {'username': 'testPerson2', 'name': 'Name2', 'surname': 'Surname2', 'password': 'test123',
             'passwordRetype': 'test123', 'email': 'test2@test.nl'})

        self.person_2.number_of_stocks = 100
        self.person_2.save()

        self.bidding_round = BiddingRound.objects.get_or_create(is_active=True)[0]

        stock_order_2 = StockOrder()
        stock_order_2.owner = self.person_2
        stock_order_2.order_type = SELL
        stock_order_2.order_amount_of_shares = 10
        stock_order_2.order_price_per_share = 8.00
        stock_order_2.bidding_round = self.bidding_round

        stock_order_3 = StockOrder()
        stock_order_3.owner = self.person_1
        stock_order_3.order_type = BUY
        stock_order_3.order_amount_of_shares = 5
        stock_order_3.order_price_per_share = 8.00
        stock_order_3.bidding_round = self.bidding_round

        stock_order_5 = StockOrder()
        stock_order_5.owner = self.person_2
        stock_order_5.order_type = SELL
        stock_order_5.order_amount_of_shares = 5
        stock_order_5.order_price_per_share = 10.00
        stock_order_5.bidding_round = self.bidding_round

        stock_order_7 = StockOrder()
        stock_order_7.owner = self.person_1
        stock_order_7.order_type = BUY
        stock_order_7.order_amount_of_shares = 10
        stock_order_7.order_price_per_share = 10.00
        stock_order_7.bidding_round = self.bidding_round

        self.order_2 = self.order_manager.place_order(stock_order_2)
        self.order_3 = self.order_manager.place_order(stock_order_3)
        self.order_5 = self.order_manager.place_order(stock_order_5)
        self.order_7 = self.order_manager.place_order(stock_order_7)

        self.order_2.order_status = DEFINITIVE
        self.order_3.order_status = DEFINITIVE
        self.order_5.order_status = DEFINITIVE
        self.order_7.order_status = DEFINITIVE

    def test_add_transaction(self):
        """
        - add sell_order and share_amount to transaction_dict
        - if entry in transaction_dict does not exist, create entry
        - if shares amount is float, use int-part and return decimal-part
        - if there are no shares left after transaction, call set_assign_complete()
        - if share_amount > shares_left, return residual_shares
        """
        sell_order = StockOrderWrapper(self.order_2)
        order_3 = StockOrderWrapper(self.order_3)
        order_7 = StockOrderWrapper(self.order_7)

        # =================================================================
        # test: OrderTypeException
        # =================================================================

        try:
            sell_order.add_transaction(sell_order=sell_order, share_amount=3)
            raise AssertionError("TransactionException expected")
        except TransactionException:
            pass

        try:
            order_3.add_transaction(sell_order=order_3, share_amount=3)
            raise AssertionError("TransactionException expected")
        except TransactionException:
            pass

        # =================================================================
        # test: add share_amount value zero to transaction_dict
        # =================================================================

        order_3.add_transaction(sell_order=sell_order, share_amount=0)
        order_7.add_transaction(sell_order=sell_order, share_amount=0)

        self.assertEquals(order_3.transaction_dict, {})
        self.assertEquals(order_7.transaction_dict, {})

        # =================================================================
        # test: add non-existing sell_order to transaction_dict
        # =================================================================

        order_3.add_transaction(sell_order=sell_order, share_amount=2)
        order_7.add_transaction(sell_order=sell_order, share_amount=1)

        self.assertEquals(order_3.transaction_dict, {sell_order: 2})
        self.assertEquals(order_7.transaction_dict, {sell_order: 1})

        # =================================================================
        # test: add existing sell_order to transaction_dict
        # =================================================================

        order_3.add_transaction(sell_order=sell_order, share_amount=1)
        order_7.add_transaction(sell_order=sell_order, share_amount=2)

        self.assertEquals(order_3.transaction_dict, {sell_order: 3})
        self.assertEquals(order_7.transaction_dict, {sell_order: 3})

        # =================================================================
        # test: use int-part and return decimal-part
        # =================================================================

        result_3 = order_3.add_transaction(sell_order=sell_order, share_amount=1.321)
        result_7 = order_7.add_transaction(sell_order=sell_order, share_amount=0.987)

        self.assertEquals(order_3.transaction_dict, {sell_order: 4})
        self.assertEquals(order_7.transaction_dict, {sell_order: 3})

        self.assertEquals(result_3, .321)
        self.assertEquals(result_7, .987)

        # =================================================================
        # test: set_assign_complete and return residual shares
        # =================================================================

        result_3 = order_3.add_transaction(sell_order=sell_order, share_amount=5)
        result_7 = order_7.add_transaction(sell_order=sell_order, share_amount=5)

        self.assertEquals(result_3, 4)
        self.assertEquals(result_7, 0.0)

        self.assertEquals(order_3.order_status, PROCESSED)
        self.assertEquals(order_7.transaction_dict, {sell_order: 8})

        result_7 = order_7.add_transaction(sell_order=sell_order, share_amount=12.432)
        self.assertEquals(result_7, 10.432)

        self.assertEquals(order_7.order_status, PROCESSED)

    def test_set_assign_complete(self):
        """
        - set stock_order result to ASSIGNED_COMPLETE
        - set stock_order status to PROCESSED
        - set stock_order_wrapper status to PROCESSED
        - save stock order
        """
        order_2 = StockOrderWrapper(self.order_2)
        order_3 = StockOrderWrapper(self.order_3)
        order_5 = StockOrderWrapper(self.order_5)
        order_7 = StockOrderWrapper(self.order_7)

        order_2.set_assign_complete()
        order_3.set_assign_complete()
        order_5.set_assign_complete()
        order_7.set_assign_complete()

        # =================================================================
        # test: order_wrapper status is updated
        # =================================================================

        self.assertEquals(order_2.order_status, PROCESSED)
        self.assertEquals(order_3.order_status, PROCESSED)
        self.assertEquals(order_5.order_status, PROCESSED)
        self.assertEquals(order_7.order_status, PROCESSED)

        # =================================================================
        # test: order is saved
        # =================================================================

        real_order_2 = StockOrder.objects.get(order_id=1)
        real_order_3 = StockOrder.objects.get(order_id=2)
        real_order_5 = StockOrder.objects.get(order_id=3)
        real_order_7 = StockOrder.objects.get(order_id=4)

        # =================================================================
        # test: order_result is updated
        # =================================================================

        self.assertEquals(real_order_2.order_result, ASSIGNED_COMPLETE)
        self.assertEquals(real_order_3.order_result, ASSIGNED_COMPLETE)
        self.assertEquals(real_order_5.order_result, ASSIGNED_COMPLETE)
        self.assertEquals(real_order_7.order_result, ASSIGNED_COMPLETE)

        # =================================================================
        # test: order_status is updated
        # =================================================================

        self.assertEquals(real_order_2.order_status, PROCESSED)
        self.assertEquals(real_order_3.order_status, PROCESSED)
        self.assertEquals(real_order_5.order_status, PROCESSED)
        self.assertEquals(real_order_7.order_status, PROCESSED)

    def test_handle_transactions(self):
        """
        * call validate_transaction
        * create and save transaction
        * return transaction
        """
        # =================================================================
        # test: add_transaction doesn't satisfies order (shares left)
        # =================================================================

        sell_order = StockOrderWrapper(self.order_5)
        buy_order = StockOrderWrapper(self.order_7)
        share_amount = 3
        share_price = self.order_5.order_price_per_share
        transaction_status = PROCESSED

        buy_order.add_transaction(sell_order=sell_order, share_amount=share_amount)

        trans_exp_7 = Transaction(buy=self.order_7, sell=self.order_5, share_amount=3,
                                  share_price=share_price, transaction_status=transaction_status)

        trans_real_7 = buy_order.handle_transactions(sell_order)

        self.is_equal_transaction(trans_real_7, trans_exp_7)
        self.assertEqual(sell_order.shares_left, 5)
        self.assertEqual(buy_order.shares_left, 7)

    def is_equal_transaction(self, real, expected):
        self.assertEquals(real.buy, expected.buy)
        self.assertEquals(real.sell, expected.sell)
        self.assertEquals(real.share_amount, expected.share_amount)
        self.assertEquals(real.share_price, expected.share_price)
        self.assertEquals(real.transaction_status, expected.transaction_status)

    def is_equal_order_wrapper(self, real, expected):
        self.assertEquals(real.stock_order, expected.stock_order)
        self.assertEquals(real.order_status, expected.order_status)
        self.assertEquals(real.transaction_dict, expected.transaction_dict)
