


def generates_payment_data(callback_query, payment_info, product, date, table_name=None, price=None):
    """Генерация данных для оплаты"""
    data = {
        "user_id": callback_query.from_user.id,  # ID пользователя в Telegram
        "first_name": callback_query.from_user.first_name,  # Имя пользователя в Telegram
        "last_name": callback_query.from_user.last_name,  # Фамилия пользователя в Telegram
        "username": callback_query.from_user.username,  # Username пользователя в Telegram
        "payment_info": payment_info,  # Информация о счете
        "product": product,  # Название товара
        "date": date,  # Дата оплаты
        "payment_status": "succeeded"  # Статус оплаты
    }
    if table_name:
        data["table_name"] = table_name
    if price:
        data["price"] = price
    return data
