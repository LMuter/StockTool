__author__ = 'laurens'


def normal_share_distribution(manager, buy_order_float_dict, sell_order):
    """
    """
    buy_orders_left = []
    for share_amount, buy_order_list in buy_order_float_dict.items():
        share_amount = int(share_amount)

        for buy_order in buy_order_list:
            manager.handle_transaction(sell_order=sell_order, buy_order=buy_order, share_amount=share_amount)

            if buy_order.shares_left:
                buy_orders_left.append(buy_order)
    return buy_orders_left


def flatten_dict(manager, buy_order_float_dict, sell_order):
    """
    """
    buy_order_date_list = []
    for float_value, buy_orders in buy_order_float_dict.items():

        share_amount = int(float_value)

        if share_amount:
            for buy_order in buy_orders:
                manager.handle_transaction(sell_order=sell_order, buy_order=buy_order, share_amount=share_amount)

                if buy_order.shares_left:
                    buy_order_date_list.append(buy_order)
    return buy_order_date_list