order_map = {}


def save_order(order_id, chat_id):

    order_map[order_id] = chat_id


def get_chat(order_id):

    return order_map.get(order_id)


def delete_order(order_id):

    if order_id in order_map:

        del order_map[order_id]
