from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def purchasing_a_program_setup_service(url, id_pay) -> InlineKeyboardMarkup:
    """Клавиатура оплаты за настройку программного обеспечения"""
    payment_keyboard_key = InlineKeyboardMarkup()
    byy_baton = InlineKeyboardButton("💳 Оплатить 500 руб.", url=url)
    check_payment = InlineKeyboardButton('Проверить оплату', callback_data=f"check_service_{id_pay}")
    payment_keyboard_key.row(byy_baton)
    payment_keyboard_key.row(check_payment)
    return payment_keyboard_key


