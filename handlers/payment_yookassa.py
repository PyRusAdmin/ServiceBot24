# -*- coding: utf-8 -*-
import json

from loguru import logger  # Логирование с помощью loguru
from yookassa import Configuration, Payment

from system.dispatcher import ACCOUNT_ID, SECRET_KEY


def payment_yookassa_com(description_text, product_price):
    """
    Оплата yookassa TelegramMaster_Commentator

    :param description_text: Описание товара
    :param product_price: Цена товара
    :return: Ссылка для оплаты, ID оплаты
    """

    Configuration.account_id = ACCOUNT_ID
    Configuration.secret_key = SECRET_KEY

    payment = Payment.create(
        {"amount": {"value": product_price,  # Стоимость товара
                    "currency": "RUB"}, "capture": True,
         "confirmation": {"type": "redirect", "return_url": "https://t.me/h24service_bot"},
         "description": description_text,
         "metadata": {'order_number': '1'},
         "receipt": {"customer": {"email": "zh.vitaliy92@yandex.ru"},
                     "items": [
                         {
                             "description": description_text,  # Название товара
                             "quantity": "1",
                             "amount": {"value": product_price,  # Стоимость товара
                                        "currency": "RUB"},  # Сумма и валюта
                             "vat_code": "1"}]}})

    payment_data = json.loads(payment.json())
    payment_id = payment_data['id']
    payment_url = (payment_data['confirmation'])['confirmation_url']
    logger.info(f"Ссылка для оплаты: {payment_url}, ID оплаты {payment_id}")
    return payment_url, payment_id
