# -*- coding: utf-8 -*-
"""
Тесты для проверки оплаты
"""
import sys
import os

# Добавляем корень проекта в path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from handlers.payments.payment_config import get_stars_amount, STARS_TO_RUB_RATE
from handlers.payments.products_goods_services import SERVER_RENT_PRICE


def test_stars_conversion():
    """Тест конвертации рублей в звезды"""
    print("=" * 50)
    print("ТЕСТ КОНВЕРТАЦИИ РУБЛЕЙ В ЗВЕЗДЫ")
    print("=" * 50)
    print(f"Курс: 1 ⭐️ = {STARS_TO_RUB_RATE} ₽")
    print()

    # Тест аренды сервера
    print("Аренда сервера:")
    for months in [1, 2, 3, 6, 12]:
        rub_price = SERVER_RENT_PRICE * months
        stars = get_stars_amount(rub_price)
        print(f"  {months} мес. = {rub_price} ₽ → {stars} ⭐️")

    print()
    print("Другие товары:")
    test_prices = [
        (500, "MaxMaster"),
        (1600, "TelegramMaster-PRO"),
        (1300, "TelegramMaster_Commentator"),
        (300, "Пароль"),
    ]

    for price, name in test_prices:
        stars = get_stars_amount(price)
        print(f"  {name}: {price} ₽ → {stars} ⭐️")

    print()
    print("=" * 50)
    print("ТЕСТ ЗАВЕРШЕН")
    print("=" * 50)


if __name__ == "__main__":
    test_stars_conversion()
