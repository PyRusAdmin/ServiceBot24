# -*- coding: utf-8 -*-
"""
Оплата через YooKassa
"""
import json

from loguru import logger
from yookassa import Configuration, Payment

from system.dispatcher import ACCOUNT_ID, SECRET_KEY

# Проверка наличия учетных данных
if not ACCOUNT_ID or not SECRET_KEY:
    logger.error("❌ YooKassa: ACCOUNT_ID и SECRET_KEY не заданы в .env файле!")
else:
    # Инициализация конфигурации YooKassa
    Configuration.account_id = ACCOUNT_ID
    Configuration.secret_key = SECRET_KEY
    logger.info(f"✅ YooKassa инициализирована (Account ID: {ACCOUNT_ID})")


def payment_yookassa_com(description_text, product_price):
    """
    Оплата программы с помощью сервиса yookassa
    
    :param description_text: Описание товара
    :param product_price: Цена товара
    :return: payment_url, payment_id
    """
    payment_config = {
        "amount": {
            "value": product_price,
            "currency": "RUB"
        },
        "capture": True,
        "confirmation": {
            "type": "redirect",
            "return_url": "https://t.me/h24service_bot"
        },
        "description": description_text,
    }
    
    payment = Payment.create(payment_config)
    payment_data = json.loads(payment.json())
    payment_id = payment_data['id']
    payment_url = payment_data['confirmation']['confirmation_url']
    
    logger.info(f"Ссылка для оплаты: {payment_url}, ID: {payment_id}")
    
    return payment_url, payment_id
