"""
Оплата через YooKassa
"""
import uuid

from loguru import logger
from yookassa import Configuration, Payment

from system.dispatcher import ACCOUNT_ID, SECRET_KEY

# Инициализация YooKassa
if ACCOUNT_ID and SECRET_KEY:
    Configuration.account_id = ACCOUNT_ID
    Configuration.secret_key = SECRET_KEY
    logger.info(f"✅ YooKassa инициализирована (Account ID: {ACCOUNT_ID})")
else:
    logger.error("❌ YooKassa: ACCOUNT_ID и SECRET_KEY не заданы!")


def payment_yookassa_com(description_text, product_price: float):
    """
    Создание платежа YooKassa
    
    :param description_text: Описание товара
    :param product_price: Цена товара
    :return: payment_url, payment_id
    """
    payment = Payment.create({
        "amount": {
            "value": product_price,
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "https://t.me/h24service_bot"
        },
        "capture": True,
        "description": description_text
    }, uuid.uuid4())

    payment_url = payment.confirmation.confirmation_url
    payment_id = payment.id

    logger.info(f"Ссылка для оплаты: {payment_url}, ID: {payment_id}")

    return payment_url, payment_id
