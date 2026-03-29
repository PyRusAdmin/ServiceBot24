# -*- coding: utf-8 -*-
"""
Оплата через YooKassa
Поддержка всех методов оплаты: https://yookassa.ru/developers/payment-acceptance/getting-started/payment-methods
"""
import json

from loguru import logger
from yookassa import Configuration, Payment

from system.dispatcher import ACCOUNT_ID, SECRET_KEY

# Проверка наличия учетных данных
if not ACCOUNT_ID or not SECRET_KEY:
    logger.error("❌ YooKassa: ACCOUNT_ID и SECRET_KEY не заданы в .env файле!")
    logger.error("Добавьте в .env файл:")
    logger.error("  ACCOUNT_ID=ваш_id")
    logger.error("  SECRET_KEY=ваш_ключ")
else:
    # Инициализация конфигурации YooKassa
    Configuration.account_id = ACCOUNT_ID
    Configuration.secret_key = SECRET_KEY
    logger.info(f"✅ YooKassa инициализирована (Account ID: {ACCOUNT_ID})")


def payment_yookassa_sbp(description_text, product_price):
    """
    Оплата через СБП (Система Быстрых Платежей)
    https://yookassa.ru/developers/payment-acceptance/getting-started/payment-methods#sbp
    
    :param description_text: Описание товара
    :param product_price: Цена товара
    :return: payment_url, payment_id, qr_code, payment_data
    """
    payment_config = {
        "amount": {
            "value": product_price,
            "currency": "RUB"
        },
        "payment_method_data": {
            "type": "sbp"  # СБП
        },
        "capture": True,
        "confirmation": {
            "type": "redirect",
            "return_url": "https://t.me/h24service_bot"
        },
        "description": description_text,
        "metadata": {'order_number': '1'},
        "receipt": {
            "customer": {"email": "zh.vitaliy92@yandex.ru"},
            "items": [
                {
                    "description": description_text,
                    "quantity": "1",
                    "amount": {
                        "value": product_price,
                        "currency": "RUB"
                    },
                    "vat_code": "1"
                }
            ]
        }
    }
    
    payment = Payment.create(payment_config)
    payment_data = json.loads(payment.json())
    payment_id = payment_data['id']
    payment_url = payment_data['confirmation']['confirmation_url']
    
    # Получаем QR-код для СБП (если доступен)
    qr_code = payment_data.get('confirmation', {}).get('confirmation_data', None)
    
    logger.info(f"СБП платеж {payment_id}: {amount} ₽, QR: {qr_code is not None}")
    
    return payment_url, payment_id, qr_code, {
        'id': payment_id,
        'url': payment_url,
        'qr_code': qr_code,
        'amount': product_price,
        'status': payment_data.get('status', 'pending'),
        'method': 'sbp'
    }


def payment_yookassa_com(description_text, product_price, payment_method=None):
    """
    Оплата программы с помощью сервиса yookassa
    Поддерживаемые методы оплаты:
    - None (все методы доступны)
    - 'bank_card' - банковская карта
    - 'yoomoney' - ЮMoney
    - 'sberbank' - Сбербанк Онлайн
    - 'tinkoff' - Тинькофф
    - 'mobile_balance' - мобильный баланс
    - 'sbp' - СБП
    - 'cash' - наличные

    :param description_text: Описание товара
    :param product_price: Цена товара
    :param payment_method: Метод оплаты (None = все методы)
    :return: Ссылка для оплаты, ID оплаты, данные платежа
    """
    # Конфигурация платежа
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
        "metadata": {'order_number': '1'},
        "receipt": {
            "customer": {"email": "zh.vitaliy92@yandex.ru"},
            "items": [
                {
                    "description": description_text,
                    "quantity": "1",
                    "amount": {
                        "value": product_price,
                        "currency": "RUB"
                    },
                    "vat_code": "1"
                }
            ]
        }
    }
    
    # Если указан конкретный метод оплаты
    if payment_method:
        payment_config["payment_method_data"] = {
            "type": payment_method
        }
    
    payment = Payment.create(payment_config)
    payment_data = json.loads(payment.json())
    payment_id = payment_data['id']
    payment_url = payment_data['confirmation']['confirmation_url']
    
    # Получаем доступные методы оплаты
    available_methods = payment_data.get('payment_method_types', [])
    
    logger.info(f"Ссылка для оплаты: {payment_url}, ID: {payment_id}, методы: {available_methods}")
    
    return payment_url, payment_id, {
        'id': payment_id,
        'url': payment_url,
        'amount': product_price,
        'status': payment_data.get('status', 'pending'),
        'methods': available_methods
    }


def check_payment_status(payment_id):
    """
    Проверка статуса платежа
    
    :param payment_id: ID платежа
    :return: Данные о платеже
    """
    try:
        payment = Payment.find_one(payment_id)
        payment_data = json.loads(payment.json())
        
        return {
            'id': payment_data['id'],
            'status': payment_data.get('status', 'unknown'),
            'amount': payment_data['amount']['value'],
            'payment_method': payment_data.get('payment_method', {}).get('type', 'unknown'),
            'created_at': payment_data.get('created_at', ''),
            'captured_at': payment_data.get('captured_at', '')
        }
    except Exception as e:
        logger.exception(f"Ошибка при проверке платежа: {e}")
        return {'id': payment_id, 'status': 'error'}
