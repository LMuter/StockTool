from django.test import TestCase
from stock_order.models import StockOrder
from stock_order.models import create_stock_order
from user_login.models import new_person, Person
from user_login import constants as person_constants
from bidding_round.models import BiddingRound
from bidding_round import constants as bidding_constants
from order_manager import OrderManager
from constants import *
from stock_order.stock_order_errors import *
from django.test import TestCase
from stock_register.controller import *
from user_login.models import *


class TestController(TestCase):
    def setUp(self):
        pass

    def test_get_transactions(self):
        # =================================================================
        # test: get_transactions no parameters
        # =================================================================

        # =================================================================
        # test: get_transactions only order parameter
        # =================================================================

        # =================================================================
        # test: get_transactions only perosn parameter
        # =================================================================

        # =================================================================
        # test: get_transactions perosn and order parameter
        # =================================================================

        pass


class StockOrderTestCase(TestCase):
    def setUp(self):
        new_person({'username': 'testPerson1', 'name': 'Name1', 'surname': 'Surname1', 'password': 'test123',
                    'passwordRetype': 'test123', 'email': 'test@test.nl'})

    def test_create_stock_order(self):
        person = Person.objects.get(user_first_name='Name1')
        StockOrder.objects.create(owner=person)

        expected_order = StockOrder()
        expected_order.owner = person

        order = StockOrder.objects.get(owner=person)

        self.is_equal_stock_order(order, expected_order)

    def is_equal_stock_order(self, real, expected):
        self.assertEquals(real.encrypted_order_id, expected.encrypted_order_id)
        self.assertEquals(real.order_amount_of_shares, expected.order_amount_of_shares)
        self.assertEquals(real.order_price_per_share, expected.order_price_per_share)
        self.assertEquals(real.order_definite_number_of_shares, expected.order_definite_number_of_shares)
        self.assertEquals(real.order_definite_price, expected.order_definite_price)
        self.assertEquals(real.is_archived, expected.is_archived)
        self.assertEquals(real.owner, expected.owner)
        self.assertEquals(real.order_type, expected.order_type)
        self.assertEquals(real.order_result, expected.order_result)
        self.assertEquals(real.order_status, expected.order_status)


class OrderManagerTest(TestCase):
    def setUp(self):
        self.order_manager = OrderManager()

        self.person_1 = new_person(
                {'username': 'testPerson1', 'name': 'Name1', 'surname': 'Surname1', 'password': 'test123',
                 'passwordRetype': 'test123', 'email': 'test1@test.nl'})

        self.person_1.number_of_stocks = 5
        self.person_1.save()

        self.person_2 = new_person(
                {'username': 'testPerson2', 'name': 'Name2', 'surname': 'Surname2', 'password': 'test123',
                 'passwordRetype': 'test123', 'email': 'test2@test.nl'})

        self.person_3 = new_person(
                {'username': 'testPerson3', 'name': 'Name3', 'surname': 'Surname3', 'password': 'test123',
                 'passwordRetype': 'test123', 'email': 'test3@test.nl'})

        self.bidding_round = BiddingRound.objects.create(is_active=True)

        stock_order_1 = StockOrder()
        stock_order_1.owner = self.person_1
        stock_order_1.order_type = BUY
        stock_order_1.order_price_per_share = 8.5
        stock_order_1.order_amount_of_shares = 10
        stock_order_1.bidding_round = self.bidding_round

        stock_order_2 = StockOrder()
        stock_order_2.owner = self.person_1
        stock_order_2.order_type = BUY
        stock_order_2.order_price_per_share = 7.5
        stock_order_2.order_amount_of_shares = 5
        stock_order_2.bidding_round = self.bidding_round

        stock_order_3 = StockOrder()
        stock_order_3.owner = self.person_1
        stock_order_3.order_type = BUY
        stock_order_3.order_price_per_share = 6.5
        stock_order_3.order_amount_of_shares = 15
        stock_order_3.bidding_round = self.bidding_round

        stock_order_arch = StockOrder()
        stock_order_arch.owner = self.person_1
        stock_order_arch.order_type = SELL
        stock_order_arch.order_price_per_share = 5
        stock_order_arch.order_amount_of_shares = 100
        stock_order_arch.bidding_round = self.bidding_round
        stock_order_arch.is_archived = True

        self.order_1_person_1 = self.order_manager.place_order(stock_order_1)
        self.order_2_person_1 = self.order_manager.place_order(stock_order_2)
        self.order_3_person_1 = self.order_manager.place_order(stock_order_3)
        self.order_archived_person_1 = create_stock_order(stock_order_arch)

        self.order_1_person_2 = StockOrder.objects.create(owner=self.person_2)
        self.order_2_person_2 = StockOrder.objects.create(owner=self.person_2)

        self.order_1_person_3 = StockOrder.objects.create(owner=self.person_2)

    def test_can_place_order(self):
        """
        checks if user can place order:
          * bidding period is active (first, second and third complete week of october)
              - first bidding round for third party and staff
              - second bidding round for staff
              - third bidding round for moderator
          * user has not exceeded his maximal bidding order number
          * total of non-archived SELL orders incl this one does not exceeded
            persons number_of_stocks (exp moderator_person)
        returns error message, None otherwise
        """
        self.person_1.number_of_orders_max = 6
        self.person_1.number_of_stocks = 50

        stock_order = StockOrder()
        stock_order.order_amount_of_shares = 10
        stock_order.owner = self.person_1
        stock_order.order_type = SELL
        # create_stock_order(stock_order)

        # =================================================================
        # test: NoBiddingRoundException
        # =================================================================

        try:
            self.order_manager.can_place_order(self.person_1, stock_order)
            raise AssertionError('NoBiddingRoundException expected')
        except NoBiddingRoundException:
            pass

        # create bidding round
        bidding_round = BiddingRound.objects.create(is_active=True)
        stock_order.bidding_round = bidding_round

        # valid order
        self.assertIsNone(self.order_manager.can_place_order(self.person_1, stock_order))

        # =================================================================
        # test: BiddingRoundNotActiveException
        # =================================================================

        bidding_round.is_active = False

        try:
            self.order_manager.can_place_order(self.person_1, stock_order)
            raise AssertionError('BiddingRoundNotActiveException expected')
        except BiddingRoundNotActiveException:
            pass

        bidding_round.is_active = True
        self.assertIsNone(self.order_manager.can_place_order(self.person_1, stock_order))

        # =================================================================
        # test: UserTypeException
        # =================================================================

        bidding_round.round_type = bidding_constants.STAFF_ROUND

        try:
            self.order_manager.can_place_order(self.person_1, stock_order)
            raise AssertionError('UserTypeException expected')
        except UserTypeException:
            pass

        self.person_1.user_type = person_constants.STAFF
        self.assertIsNone(self.order_manager.can_place_order(self.person_1, stock_order))

        bidding_round.round_type = bidding_constants.MODERATOR_ROUND

        try:
            self.order_manager.can_place_order(self.person_1, stock_order)
            raise AssertionError('UserTypeException expected')
        except UserTypeException:
            pass

        self.person_1.user_type = person_constants.MODERATOR
        self.assertIsNone(self.order_manager.can_place_order(self.person_1, stock_order))

        self.person_1.user_type = person_constants.THIRD_PARTY

        try:
            self.order_manager.can_place_order(self.person_1, stock_order)
            raise AssertionError('UserTypeException expected')
        except UserTypeException:
            pass

        bidding_round.round_type = bidding_constants.THIRD_PARTY_ROUND
        self.assertIsNone(self.order_manager.can_place_order(self.person_1, stock_order))

        # =================================================================
        # test: ExceedMaxSellSharesException
        # =================================================================

        stock_order.order_amount_of_shares = 51

        try:
            self.order_manager.can_place_order(self.person_1, stock_order)
            raise AssertionError('ExceedMaxSellSharesException expected')
        except ExceedMaxSellSharesException:
            pass

        stock_order.order_amount_of_shares = 49

        self.assertIsNone(self.order_manager.can_place_order(self.person_1, stock_order))

        stock_order_4 = StockOrder()
        stock_order_4.owner = self.person_1
        stock_order_4.order_type = SELL
        stock_order_4.order_price_per_share = 5.5
        stock_order_4.bidding_round = self.bidding_round
        stock_order_4.order_amount_of_shares = 1

        self.order_manager.place_order(stock_order_4)

        self.assertIsNone(self.order_manager.can_place_order(self.person_1, stock_order))

        stock_order_5 = StockOrder()
        stock_order_5.owner = self.person_1
        stock_order_5.order_type = SELL
        stock_order_5.bidding_round = self.bidding_round
        stock_order_5.order_amount_of_shares = 1
        stock_order_5.order_price_per_share = 8.5

        self.order_manager.place_order(stock_order_5)

        try:
            self.order_manager.can_place_order(self.person_1, stock_order)
            raise AssertionError('ExceedMaxSellSharesException expected')
        except ExceedMaxSellSharesException:
            pass

        # =================================================================
        # test: ExceedMaxOrderException
        # =================================================================

        stock_order.order_type = BUY

        stock_order_5 = StockOrder()
        stock_order_5.owner = self.person_1
        stock_order_5.order_type = BUY
        stock_order_5.bidding_round = self.bidding_round
        stock_order_5.order_amount_of_shares = 50
        stock_order_5.order_price_per_share = 6.5

        self.order_manager.place_order(stock_order_5)

        try:
            self.order_manager.can_place_order(self.person_1, stock_order)
            raise AssertionError('ExceedMaxOrderException expected')
        except ExceedMaxOrderException:
            pass

    def test_is_valid_order(self):
        """
        checks if stock order is valid:
          * order must have a order_type BUY or SELL
          * order must have order_price_per_share (float)
          * order must have order_amount_of_shares (int)
          * order must have owner (Person)
        returns error message, None otherwise
        """
        stock_order = StockOrder()
        stock_order.order_type = BUY
        stock_order.order_price_per_share = 5.5
        stock_order.order_amount_of_shares = 10
        stock_order.bidding_round = self.bidding_round

        # =================================================================
        # test: OwnerNotFoundException
        # =================================================================

        try:
            self.order_manager.is_valid_order(stock_order)
            raise AssertionError('OwnerNotFoundException expected')
        except OwnerNotFoundException:
            pass

        stock_order.owner = self.person_1

        self.assertIsNone(self.order_manager.is_valid_order(stock_order))

        # =================================================================
        # test: InvalidOrderTypeException
        # =================================================================

        stock_order.order_type = UNDEFINED

        try:
            self.order_manager.is_valid_order(stock_order)
            raise AssertionError('InvalidOrderTypeException expected')
        except InvalidOrderTypeException:
            pass

        stock_order.order_type = SELL
        self.assertIsNone(self.order_manager.is_valid_order(stock_order))

        # =================================================================
        # test: OrderPriceTypeException
        # =================================================================

        stock_order.order_price_per_share = "0.01"

        try:
            self.order_manager.is_valid_order(stock_order)
            raise AssertionError('OrderPriceTypeException expected')
        except OrderPriceTypeException:
            pass

        stock_order.order_price_per_share = 123456789012345678901234567890

        try:
            self.order_manager.is_valid_order(stock_order)
            raise AssertionError('OrderPriceTypeException expected')
        except OrderPriceTypeException:
            pass

        stock_order.order_price_per_share = 2312.34
        self.assertIsNone(self.order_manager.is_valid_order(stock_order))

        # =================================================================
        # test: OrderShareAmountException
        # =================================================================

        stock_order.order_amount_of_shares = "0.01"

        try:
            self.order_manager.is_valid_order(stock_order)
            raise AssertionError('OrderShareAmountException expected')
        except OrderShareAmountException:
            pass

        stock_order.order_amount_of_shares = 123456789012345678901234567890

        try:
            self.order_manager.is_valid_order(stock_order)
            raise AssertionError('OrderShareAmountException expected')
        except OrderShareAmountException:
            pass

        stock_order.order_amount_of_shares = 2312.34

        try:
            self.order_manager.is_valid_order(stock_order)
            raise AssertionError('OrderShareAmountException expected')
        except OrderShareAmountException:
            pass

        stock_order.order_amount_of_shares = 23120
        self.assertIsNone(self.order_manager.is_valid_order(stock_order))

    def test_place_order(self):
        stock_order_4 = StockOrder()
        stock_order_4.owner = self.person_1
        stock_order_4.order_type = SELL
        stock_order_4.bidding_round = self.bidding_round
        stock_order_4.is_archived = True
        stock_order_4.order_amount_of_shares = 5
        stock_order_4.order_definite_number_of_shares = 4
        stock_order_4.order_definite_price = 12.5321
        stock_order_4.order_price_per_share = 24.5321
        stock_order_4.order_result = ASSIGNED_PARTIAL
        stock_order_4.order_status = USER_ACCEPTED

        stock_order_created = self.order_manager.place_order(stock_order_4)

        # check values
        self.is_equal_stock_order(stock_order_4, stock_order_created)
        self.assertEquals(len(stock_order_created.encrypted_order_id), 32)

        # =================================================================
        # test: PlaceOrderException
        # =================================================================

        stock_order_4.order_amount_of_shares = 10

        try:
            self.order_manager.place_order(stock_order_4)
            raise AssertionError('PlaceOrderException expected')
        except PlaceOrderException:
            pass

    def test_accept_oder(self):

        # =================================================================
        # test: increase / decrease stock numbers and status
        # =================================================================

        self.assertEquals(self.person_1.number_of_orders_accepted, 0)
        self.assertEquals(self.person_1.number_of_orders_pending, 3)

        encrypted_order_id = self.order_1_person_1.encrypted_order_id
        stock_order = StockOrder.objects.get(owner=self.person_1, encrypted_order_id=encrypted_order_id)

        self.assertEquals(stock_order.order_status, NEW)

        self.order_manager.accept_oder(self.person_1, encrypted_order_id)

        self.assertEquals(self.person_1.number_of_orders_accepted, 1)
        self.assertEquals(self.person_1.number_of_orders_pending, 2)

        stock_order = StockOrder.objects.get(owner=self.person_1, encrypted_order_id=encrypted_order_id)

        self.assertEquals(stock_order.order_status, USER_ACCEPTED)

        # =================================================================
        # test: AlreadyAcceptedException
        # =================================================================

        try:
            self.order_manager.accept_oder(self.person_1, encrypted_order_id)
            raise AssertionError('AlreadyAcceptedException expected')
        except AlreadyAcceptedException:
            pass

        # second time accept_oder should have no consequence

        self.assertEquals(self.person_1.number_of_orders_accepted, 1)
        self.assertEquals(self.person_1.number_of_orders_pending, 2)

        stock_order = StockOrder.objects.get(owner=self.person_1, encrypted_order_id=encrypted_order_id)

        self.assertEquals(stock_order.order_status, USER_ACCEPTED)

        # =================================================================
        # test: OrderNotFoundException
        # =================================================================

        try:
            self.order_manager.accept_oder(self.person_1, "XXX")
            raise AssertionError('OrderNotFoundException expected')
        except OrderNotFoundException:
            pass

        try:
            self.order_manager.accept_oder(self.person_2, encrypted_order_id)
            raise AssertionError('OrderNotFoundException expected')
        except OrderNotFoundException:
            pass

        # =================================================================
        # test: OrderIsArchivedException
        # =================================================================

        encrypted_order_id = self.order_archived_person_1.encrypted_order_id
        stock_order = StockOrder.objects.get(owner=self.person_1, encrypted_order_id=encrypted_order_id)

        try:
            self.order_manager.accept_oder(self.person_1, encrypted_order_id)
            raise AssertionError('OrderIsArchivedException expected')
        except OrderIsArchivedException:
            pass

        self.is_equal_stock_order(self.order_archived_person_1, stock_order)

    def is_equal_stock_order(self, real, expected):
        self.assertEquals(real.order_amount_of_shares, expected.order_amount_of_shares)
        self.assertEquals(real.order_price_per_share, expected.order_price_per_share)
        self.assertEquals(real.order_definite_number_of_shares, expected.order_definite_number_of_shares)
        self.assertEquals(real.order_definite_price, expected.order_definite_price)
        self.assertEquals(real.is_archived, expected.is_archived)
        self.assertEquals(real.owner, expected.owner)
        self.assertEquals(real.order_type, expected.order_type)
        self.assertEquals(real.order_result, expected.order_result)
        self.assertEquals(real.order_status, expected.order_status)


class StockOrderHelperTestCase(TestCase):
    def setUp(self):
        pass

    def test_get_total_sell_stock_amount(self):
        # get all stock orders of type SELL from person
        # exclude archived stock orders
        # sum order_amount_of_shares
        # if no orders are found, return 0
        # if person does not exist, return 0

        # get_total_sell_stock_amount(person)
        pass
