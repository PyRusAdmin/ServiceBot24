from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def payment_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура оплаты TelegramMaster"""
    rows = [
        [InlineKeyboardButton(text=f"💳 Оплатить (Юкасса)", callback_data='payment_yookassa_program'),
         InlineKeyboardButton(text=f"💳 Оплатить (Крипта)", callback_data=f"payment_crypta_pas_program"),
         ],
        [InlineKeyboardButton(text='В начальное меню', callback_data='start_menu_keyboard')],

        # [InlineKeyboardButton(text='Проверить оплату (Юкасса)', callback_data=f"check_payment_{id_pay}")],

        # [InlineKeyboardButton(text=f"💳 Оплатить (Крипта)",
        #                       callback_data=f"payment_crypta_pas_program")],
    ]

    payment_keyboard_key = InlineKeyboardMarkup(inline_keyboard=rows)

    return payment_keyboard_key
