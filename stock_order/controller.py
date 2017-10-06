from constants import *
from stock_order.order_manager import OrderManager


def get_transactions(person=None, stock_order=None):
    transaction_dict = {}

    return transaction_dict


def get_user_statistics(person):
    user_stats = {}

    order_manager = OrderManager()
    total_value_sell = order_manager.get_order_total_value(order_type="SELL", order_status=DEFINITIVE)
    total_amount_sell = order_manager.get_order_total_amount(order_type="SELL", order_status=DEFINITIVE)

    total_value_buy = order_manager.get_order_total_value(order_type="BUY", order_status=DEFINITIVE)
    total_amount_buy = order_manager.get_order_total_amount(order_type="BUY", order_status=DEFINITIVE)

    user_total_value_sell = order_manager.get_order_total_value(person=person, order_type="SELL",
                                                                order_status=DEFINITIVE)
    user_total_amount_sell = order_manager.get_order_total_amount(person=person, order_type="SELL",
                                                                  order_status=DEFINITIVE)

    user_total_value_buy = order_manager.get_order_total_value(person=person, order_type="BUY", order_status=DEFINITIVE)
    user_total_amount_buy = order_manager.get_order_total_amount(person=person, order_type="BUY",
                                                                 order_status=DEFINITIVE)

    user_stats["orders_placed_total"] = order_manager.count_orders(order_status=DEFINITIVE)
    orders_placed_buy = order_manager.count_orders(order_status=DEFINITIVE, order_type=BUY)
    orders_placed_sell = order_manager.count_orders(order_status=DEFINITIVE, order_type=SELL)

    user_stats["orders_placed_by_user"] = order_manager.count_orders(person=person, order_status=DEFINITIVE)
    orders_placed_user_buy = order_manager.count_orders(person=person, order_status=DEFINITIVE, order_type=BUY)
    orders_placed_user_sell = order_manager.count_orders(person=person, order_status=DEFINITIVE, order_type=SELL)

    user_stats["orders_placed_user_buy"] = orders_placed_user_buy if orders_placed_user_buy else 0
    user_stats["orders_placed_user_sell"] = orders_placed_user_sell if orders_placed_user_sell else 0
    user_stats["orders_placed_buy"] = orders_placed_buy if orders_placed_buy else 0
    user_stats["orders_placed_sell"] = orders_placed_sell if orders_placed_sell else 0

    user_stats["av_order_price_user_sell"] = round(float(user_total_value_sell) / user_total_amount_sell,
                                                   2) if orders_placed_user_sell else 0

    user_stats["av_order_price_user_buy"] = round(float(user_total_value_buy) / user_total_amount_buy,
                                                  2) if orders_placed_user_buy else 0

    user_stats["av_order_price_buy"] = round(float(total_value_buy) / total_amount_buy,
                                             2) if orders_placed_buy else 0

    user_stats["av_order_price_sell"] = round(float(total_value_sell) / total_amount_sell,
                                              2) if orders_placed_sell else 0

    user_stats["user_orders_left"] = person.number_of_orders_max - person.number_of_orders_total

    return user_stats


