__author__ = 'laurens'

from bidding_round.bidding_round_errors import *
from bidding_round.models import BiddingRound
from stock_order.constants import *
from stock_order.models import StockOrder
from stock_order.models import Transaction
from stock_order.stock_order_errors import ExceedMaxSellSharesException
from stock_register.models import Stock


# todo run via daemon

class ExchangeManager():
    def __init__(self):
        pass

    def get_transactions(self, bidding_rounds=None):
        transactions_all = []
        if bidding_rounds:
            for bidding_round in bidding_rounds:
                if bidding_round.is_active:
                    transactions_all += self.transactions_no_save(bidding_rounds=[bidding_round])
                else:
                    transactions_all += self.retrieve_transactions(bidding_round)
        return sorted(transactions_all, key=lambda x: (x.sell.owner.user_last_name, x.sell.owner.user_first_name,
                                                       x.buy.owner.user_last_name, x.buy.owner.user_first_name))

    @staticmethod
    def retrieve_transactions(bidding_round):
        transactions = []
        orders = StockOrder.objects.filter(bidding_round=bidding_round)
        for order in orders:
            if order.order_type == SELL:
                transactions += list(Transaction.objects.filter(sell=order))
            elif order.order_type == BUY:
                transactions += list(Transaction.objects.filter(sell=order))
        return transactions

    def filter_third_party_orders(self, orders, bidding_round):
        filtered_orders = []
        for order in orders:
            if order.shares_left > 0 and self._in_third_party_round(order, bidding_round):
                filtered_orders.append(order)
        return filtered_orders

    def filter_staff_orders(self, orders, bidding_round):
        filtered_orders = []
        for order in orders:
            if order.shares_left > 0 and self._in_staff_round(order, bidding_round):
                filtered_orders.append(order)
        return filtered_orders

    def filter_moderator_orders(self, orders, bidding_round):
        filtered_orders = []
        for order in orders:
            if order.shares_left > 0 and self._in_moderator_round(order, bidding_round):
                filtered_orders.append(order)
        return filtered_orders

    @staticmethod
    def _in_third_party_round(order, bidding_round):
        return bidding_round.start_date_third_party < order.stock_order.order_date < bidding_round.end_date_third_party

    @staticmethod
    def _in_staff_round(order, bidding_round):
        return bidding_round.start_date_staff < order.stock_order.order_date < bidding_round.end_date_staff

    @staticmethod
    def _in_moderator_round(order, bidding_round):
        return bidding_round.start_date_moderator < order.stock_order.order_date < bidding_round.end_date_moderator

    def handle_transactions(self, bidding_rounds=None, save_transactions=True):
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
        * validate result:
            - sum buy transactions should be equal to sum sell transactions
            - sum buy transactions should be equal to definitive share amount buy order
            - sum sell transactions should be equal to definitive share amount sell order
        * return transaction_list
        """

        if not bidding_rounds:
            bidding_rounds = BiddingRound.objects.filter(is_active=True)

        transactions_all = []
        for bidding in bidding_rounds:
            sell_orders = StockOrder.objects.filter(order_type=SELL, bidding_round=bidding, order_status=DEFINITIVE)
            buy_orders = StockOrder.objects.filter(order_type=BUY, bidding_round=bidding, order_status=DEFINITIVE)

            sell_order_wrappers = []
            for sell in sell_orders:
                sell_order_wrappers.append(StockOrderWrapper(sell))

            buy_order_wrappers = []
            for buy in buy_orders:
                buy_order_wrappers.append(StockOrderWrapper(buy))

            transactions = []

            # all buy orders from employer in employer_round
            # all buy orders from employer or third_party in moderation_round
            buy_order_employer = self.filter_staff_orders(buy_order_wrappers, bidding)
            buy_order_moderation = self.filter_moderator_orders(buy_order_wrappers, bidding)
            buy_order_employer_moderator = buy_order_employer + buy_order_moderation

            if len(buy_order_employer_moderator) > 0 and len(sell_order_wrappers) > 0:
                transactions += self.exchange_round(sell_orders=sell_order_wrappers,
                                                   buy_orders=buy_order_employer_moderator)

            # all buy orders from third party in third_party_round
            buy_order_third_party = self.filter_third_party_orders(buy_order_wrappers, bidding)

            if len(buy_order_third_party) > 0 and len(sell_order_wrappers) > 0:
                transactions += self.exchange_round(sell_orders=sell_order_wrappers, buy_orders=buy_order_third_party)

            if save_transactions:
                self.check_valid_persons_update(transactions)
                self.save_transactions(transactions, bidding, buy_orders, sell_orders)
                bidding.is_active = False
                bidding.save()

            transactions_all += transactions

        return transactions_all

    @staticmethod
    def exchange_stocks(transaction):
        seller = transaction.sell.owner
        buyer = transaction.buy.owner
        amount = transaction.share_amount

        stock_query = Stock.objects.filter(owner=seller)[:amount]

        for stock in stock_query:
            stock.owner = buyer
            stock.transactions.add(transaction)
            stock.save()

    @staticmethod
    def save_order(order):
        transactions = []

        if order.order_type == BUY:
            transactions = Transaction.objects.filter(buy=order)
        elif order.order_type == SELL:
            transactions = Transaction.objects.filter(sell=order)

        order.order_definite_number_of_shares = sum(t.share_amount for t in transactions)
        order.order_definite_price = sum(t.share_price * t.share_amount for t in transactions)

        order.order_status = PROCESSED

        if order.order_definite_number_of_shares == order.order_amount_of_shares:
            order.order_result = ASSIGNED_COMPLETE
        elif order.order_definite_number_of_shares == 0:
            order.order_result = REJECTED
        else:
            order.order_result = ASSIGNED_PARTIAL

        order.save()

    @staticmethod
    def update_persons_info(bidding_round):
        stock_orders = StockOrder.objects.filter(bidding_round=bidding_round)
        for stock_order in stock_orders:

            person = stock_order.owner

            if stock_order.order_type == BUY:
                number_of_stocks = person.number_of_stocks + stock_order.order_definite_number_of_shares
            elif stock_order.order_type == SELL:
                number_of_stocks = person.number_of_stocks - stock_order.order_definite_number_of_shares
            else:
                number_of_stocks = person.number_of_stocks

            pending = person.number_of_orders_pending - 1
            final = person.number_of_orders_final + 1
            total = person.number_of_orders_total - 1
            accepted = person.number_of_orders_accepted - 1

            stock_order.owner.number_of_stocks = number_of_stocks
            stock_order.owner.number_of_orders_pending = pending
            stock_order.owner.number_of_orders_final = final
            stock_order.owner.number_of_orders_total = total
            stock_order.owner.number_of_orders_accepted = accepted
            stock_order.owner.save()
            stock_order.save()

    def check_valid_persons_update(self, transactions):
        seller_amount_dict = {}
        for transaction in transactions:
            seller = transaction.sell.owner
            if seller_amount_dict.get(seller):
                seller_amount_dict[seller] += transaction.share_amount
            else:
                seller_amount_dict[seller] = transaction.share_amount

        self._is_valid_persons_update(seller_amount_dict)

    @staticmethod
    def _is_valid_persons_update(seller_amount_dict):
        for seller in seller_amount_dict.keys():
            if seller.number_of_stocks < seller_amount_dict.get(seller):
                raise ExceedMaxSellSharesException('One or more SELL-orders exceeds users total number of shares.')

    def save_transactions(self, transactions, bidding_round, buy_orders, sell_orders):
        for transaction in transactions:
            transaction.save()
            self.exchange_stocks(transaction)

        for order in buy_orders:
            self.save_order(order)

        for order in sell_orders:
            self.save_order(order)

        self.update_persons_info(bidding_round)
        bidding_round.round_type = PROCESSED
        bidding_round.save()

    def transactions_no_save(self, bidding_rounds=None):
        transactions = self.handle_transactions(bidding_rounds=bidding_rounds, save_transactions=False)
        return sorted(transactions, key=lambda x: (x.sell.owner.user_last_name, x.buy.owner.user_last_name))

    def exchange_round(self, sell_orders, buy_orders):
        """
        * create buy_order_left_list
        * sort BUY-orders (lowest price first)
        * BUY-order with price lower then lowest SELL order get order_result REJECTED
        * distribute shares:
            - SELL and BUY orders with status PROCESSED or WITHDRAWN are ignored
            - iterate over SELL-orders, per SELL order:
                o get all BUY-orders with price < SELL-order price, update status: PROCESSED, result: ASSIGNED_PARTIAL
                o get BUY-orders, higher/equal price (no status WITHDRAWN or PROCESSED), call share_distributor
                o merge returned buy_order_left_list of share_distributor with buy_order_left_list
        * return buy_order_left_list
        """
        if len(sell_orders) == 0 or len(buy_orders) == 0:
            raise BiddingRoundException("No definitive Buy or Sell orders found.")

        # create sell order dict
        sell_order_dict = _create_price_order_dict(sell_orders)

        # create and sort sell_orders_price
        sell_orders_price = sell_order_dict.keys()
        sell_orders_price.sort()
        sell_order_lowest = sell_orders_price[0]

        buy_order_list = []

        for buy_order in buy_orders:
            buy_price = buy_order.stock_order.order_price_per_share

            if buy_price >= sell_order_lowest:
                buy_order_list.append(buy_order)

        transactions_all = []

        # iterate over sell_order, handle transactions
        for sell_price in sell_orders_price:
            sell_order_list = sell_order_dict[sell_price]
            buy_order_list, transactions = _filter_buy_list(buy_order_list, sell_price)
            transactions_all += transactions
            self.share_distributor(sell_orders=sell_order_list, buy_orders=buy_order_list)

        for order in buy_orders:
            transactions_all += order.handle_all_transactions()
            # order.result = ASSIGNED_PARTIAL

        for order in sell_orders:
            transactions_all += order.handle_all_transactions()

        return transactions_all

    def share_distributor_date(self, sell_orders, buy_orders_list, split_shares):
        """
        Every buy_order has to have share_left of at least extra + 1
        return list of buy_order who have not status PROCESSED
        """
        split_shares = int(split_shares)
        residual_buy_orders = buy_orders_list[split_shares:]

        # sort buy_orders_list
        buy_orders_list.sort(key=lambda order: order.stock_order.order_date, reverse=False)

        for n in range(split_shares):
            buy_order = buy_orders_list[n]

            _transaction_distributor(sell_orders, buy_order, share_amount=1)

            if buy_order.shares_left > 0:
                residual_buy_orders.append(buy_order)

        return residual_buy_orders

    def share_distributor_float(self, min_orders, buy_order_float_dict, split_shares):
        # todo review comment-string
        """
        """
        split_shares = round(split_shares)

        max_float = buy_order_float_dict.get_max_key()
        max_float_list = buy_order_float_dict.get_max_key_entry()

        if split_shares >= len(max_float_list):
            residual_shares = 0
            for max_order in max_float_list:
                residual_shares += _transaction_distributor(min_orders, max_order, 1)

                split_shares -= (1 - residual_shares)

            buy_order_float_dict.remove_max_key()

            if split_shares:
                return self.share_distributor_float(min_orders, buy_order_float_dict, split_shares)

            return buy_order_float_dict.flatten_dict()

        else:
            date_rest = self.share_distributor_date(min_orders, max_float_list, split_shares)
            float_rest = buy_order_float_dict.flatten_dict(exclude_keys=[max_float])
            return date_rest + float_rest

    def share_distributor(self, sell_orders, buy_orders):
        # todo review comment-string
        """
        min( sum(sell_orders) and sum(buy_orders) )
        over de gekozen order_set komen de distributies en worden de orders afgehandeld
        handle_transactions wordt complexer omdat rekening gehouden moet worden met buy en sell

        * create transaction_list
        * divide sell_order share_amount over buy_order in ratio of share_amount
        * round to whole shares, biggest decimal part first on equal use placement date
        * if shares are exchanged, call handle_transaction per exchange add returned object to transaction_list
        * if shares_left of order is 0, set status to PROCESSED and order_result ASSIGNED_COMPLETE
        * return list of unsatisfied buy_orders (could be empty)
        """
        float_dict = OrderDict()
        sell_amount = float(_get_sum_shares_left(sell_orders))  # sell_order.shares_left
        buy_amount_total = float(_get_sum_shares_left(buy_orders))
        float_total = 0
        min_amount = min(sell_amount, buy_amount_total)
        max_amount = max(sell_amount, buy_amount_total)

        min_orders = sell_orders
        max_orders = buy_orders

        if buy_amount_total < sell_amount:
            min_orders = buy_orders
            max_orders = sell_orders

        for max_order in max_orders:

            share_amount = round(max_order.shares_left / max_amount * min_amount, 6)
            float_total += _transaction_distributor(min_orders, max_order, share_amount)

            if max_order.shares_left > 0:
                float_dict.add_order(key=share_amount, order=max_order)

        if float_dict.has_content() and float_total != 0:
            self.share_distributor_float(min_orders=min_orders, buy_order_float_dict=float_dict,
                                         split_shares=float_total)

        return float_dict.flatten_dict()


def _filter_buy_list(buy_orders_list, sell_price):
    """
    """
    filtered_buy_list = []
    transactions = []

    for buy_order in buy_orders_list:
        if buy_order.stock_order.order_price_per_share >= sell_price and buy_order.shares_left > 0:
            filtered_buy_list.append(buy_order)
        else:
            buy_order.handle_all_transactions()

    return filtered_buy_list, transactions


def _create_price_order_dict(orders):
    """
    return dict, order price as key and order list as value (matching order price)
    """
    order_dict = {}

    for sell_order in orders:
        price = sell_order.stock_order.order_price_per_share

        if order_dict.get(price):
            order_dict[price].append(sell_order)
        else:
            order_dict[price] = [sell_order]

    return order_dict


def _get_sum_shares_left(orders):
    """
    return sum shares left of given order
    """
    sum_shares_left = 0

    for order in orders:
        sum_shares_left += order.shares_left

    return sum_shares_left


def _transaction_distributor(min_orders, max_order, share_amount):
    """
    - distribute shares from multiple sell_orders to one buy_order
    - return float-part plus residual shares
    """
    float_total = 0

    for min_order in min_orders:

        order_amount = min([share_amount, min_order.shares_left])

        # only add transactions to buy order
        if max_order.stock_order.order_type == BUY:
            float_total += max_order.add_transaction(min_order, order_amount)
            min_order.shares_left -= int(order_amount)
        else:
            float_total += min_order.add_transaction(max_order, order_amount)
            max_order.shares_left -= int(order_amount)

        share_amount -= order_amount

        if share_amount <= 0:
            break

    if share_amount > 0:
        float_total += share_amount

    return float_total


def validate_transaction(sell_order, buy_order, share_amount):
    """
    * check if buy and sell order belong to same bidding_round-object
    * check if bidding round is active
    * check if buy-order-price-per-share is higher then sell-order-price-per-share
    * check if both buy and sell order have status DEFINITIVE
    * check if sell order has enough shares for transaction (share amount)
    * check if buy order has enough shares to buy for transaction (share amount)
    """
    bidding_round_sell = sell_order.bidding_round
    bidding_round_buy = buy_order.bidding_round

    if share_amount <= 0:
        raise ShareAmountException("Share amount should be more then 0.")

    if sell_order.order_type != SELL or buy_order.order_type != BUY:
        raise OrderTypeException("Sell_order type should be SELL and buy_order type should be BUY")

    if bidding_round_sell != bidding_round_buy:
        raise BiddingRoundException("Sell- and buy-order should be in the same bidding round.")

    if not bidding_round_sell.is_active:
        raise InactiveBiddingRoundException("Bidding round should be active.")

    price_sell = sell_order.order_price_per_share
    price_buy = buy_order.order_price_per_share

    if price_sell > price_buy:
        raise SharePriceException("Sell price can't be higher then buy price.")

    if (sell_order.order_status != DEFINITIVE) or (buy_order.order_status != DEFINITIVE):
        raise OrderStatusException("Sell- and buy-order should both be DEFINITIVE.")

    if (sell_order.order_amount_of_shares < share_amount) or (buy_order.order_amount_of_shares < share_amount):
        raise ShareAmountException("Sell- and buy-order should both have enough share.")

    return None


class StockOrderWrapper():
    def __init__(self, stock_order=None, shares_left=None):
        self.stock_order = stock_order
        self.order_status = stock_order.order_status
        self.transaction_dict = {}

        if shares_left:
            self.shares_left = shares_left
        else:
            self.shares_left = self.stock_order.order_amount_of_shares

    def set_assign_complete(self):
        """
        - set stock_order result to ASSIGNED_COMPLETE
        - set stock_order status to PROCESSED
        - set stock_order_wrapper status to PROCESSED
        - save stock order
        """
        self.stock_order.order_result = ASSIGNED_COMPLETE
        self.stock_order.order_status = PROCESSED
        self.order_status = PROCESSED
        self.stock_order.save()

    def add_transaction(self, sell_order, share_amount):
        """
        - add sell_order and share_amount to transaction_dict
        - if entry in transaction_dict does not exist, create entry
        - if shares amount is float, use int-part and return decimal-part
        - if there are no shares left after transaction, call set_assign_complete()
        - if so return residual_shares
        """
        residual_shares = share_amount - int(share_amount)
        share_amount = int(share_amount)
        if share_amount >= self.shares_left:
            residual_shares += share_amount - self.shares_left
            self._put_transaction(sell_order, self.shares_left)
            self.shares_left = 0
            self.order_status = PROCESSED
        else:
            self._put_transaction(sell_order, share_amount)
            self.shares_left -= share_amount
        return round(residual_shares, 6)

    def _put_transaction(self, sell_order, share_amount):
        if share_amount > 0:
            self._sanity_check(sell_order, share_amount)

            if sell_order in self.transaction_dict.keys():
                self.transaction_dict[sell_order] += share_amount
            else:
                self.transaction_dict[sell_order] = share_amount

    def _sanity_check(self, order, share_amount):
        try:
            if self.stock_order.order_type == BUY:
                validate_transaction(sell_order=order.stock_order, buy_order=self.stock_order,
                                     share_amount=share_amount)
            else:
                validate_transaction(sell_order=self.stock_order, buy_order=order.stock_order,
                                     share_amount=share_amount)
        except Exception as e:
            raise TransactionException(e)

    def handle_all_transactions(self):
        transactions = []
        for sell_order in self.transaction_dict.keys():
            transactions.append(self.handle_transactions(sell_order))
        return transactions

    def handle_transactions(self, sell_order):
        """
        * call validate_transaction
        * create and save transaction
        * return transaction
        """
        share_amount = self.transaction_dict.get(sell_order)
        if share_amount:
            self._sanity_check(sell_order, share_amount)
            price = sell_order.stock_order.order_price_per_share
            transaction = Transaction(buy=self.stock_order, sell=sell_order.stock_order,
                                      share_amount=share_amount, share_price=price,
                                      transaction_status=PROCESSED)
            # transaction.save()
            # del(self.transaction_dict[sell_order])
            return transaction

    def __unicode__(self):
        return unicode(
            "<StockOrderWrapper BUY: " + str(self.stock_order.order_id) + ' STATUS: ' + str(self.order_status) +
            " SHARES LEFT: " + str(self.shares_left) + ">")

    def __str__(self):
        return self.__unicode__()

    def __repr__(self):
        return self.__unicode__()


class OrderDict():
    def __init__(self):
        self.order_dict = {}
        self.max_key = 0
        self.key_list = []

    def add_order(self, key, order):
        """
        - make key smaller then one
        - add key to dict, if entry does not exist, create entry
        """
        if key >= 1:
            key = round(key - int(key), 6)

        if key not in self.key_list:
            self.key_list.append(key)

        if key in self.order_dict.keys():
            self.order_dict[key].append(order)

        else:
            if key > self.max_key:
                self.max_key = key
            self.order_dict[key] = [order]

    def get_max_key(self):
        """
        return max_key, updated when order of entry is deleted
        """
        return self.max_key

    def get_max_key_entry(self):
        """
        return entry from max_key
        """
        return self.order_dict.get(self.max_key)

    def has_content(self):
        """
        return true if order_dict has at least one entry, false otherwise
        """
        if self.order_dict:
            return True
        return False

    def remove_max_key(self):
        self.key_list.remove(self.max_key)
        self.max_key = max(self.key_list)

    def flatten_dict(self, exclude_keys=None):
        """
        - place all orders from order_dict in list
        - skip processed and excluded orders
        """
        if not exclude_keys:
            exclude_keys = []

        order_list = []

        for key in self.order_dict:
            if key not in exclude_keys:
                for order in self.order_dict[key]:
                    order_list.append(order)
        return order_list

    def __unicode__(self):
        return unicode(
            "<OrderDict " + str(self.order_dict) + ">")

    def __str__(self):
        return self.__unicode__()

    def __repr__(self):
        return self.__unicode__()
