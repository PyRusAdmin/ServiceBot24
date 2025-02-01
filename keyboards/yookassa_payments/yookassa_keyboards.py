from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from handlers.payments.products_goods_services import password_TelegramMaster


def payment_keyboard_password(url, id_pay) -> InlineKeyboardMarkup:
    """Клавиатура оплаты пароля"""
    rows = [
        [InlineKeyboardButton(text=f"💳 Оплатить {password_TelegramMaster} руб. (Юкасса)", url=url)],
        [InlineKeyboardButton(text='Проверить оплату (Юкасса)', callback_data=f"payment_pass_{id_pay}")],

        [InlineKeyboardButton(text=f"💳 Оплатить {password_TelegramMaster} руб. (Крипта)",
                              callback_data=f"payment_crypta_pas")],
    ]

    payment_keyboard_password_key = InlineKeyboardMarkup(inline_keyboard=rows)

    return payment_keyboard_password_key
