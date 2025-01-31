from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from handlers.payments.products_goods_services import payment_installation


def purchasing_a_program_setup_service(url, id_pay) -> InlineKeyboardMarkup:
    """Клавиатура оплаты за настройку программного обеспечения"""
    rows = [
        [
            InlineKeyboardButton(text=f"💳 Оплатить {payment_installation} руб.", url=url),
            InlineKeyboardButton(text='Проверить оплату', callback_data=f"check_service_{id_pay}"),
        ],

        [InlineKeyboardButton(text=f"💳 Оплатить {payment_installation} руб. (Крипта)",
                              callback_data=f"payment_crypta_pas_training_handler")],

        [InlineKeyboardButton(text='В начальное меню', callback_data='start_menu')],
    ]

    payment_keyboard_key = InlineKeyboardMarkup(inline_keyboard=rows)

    return payment_keyboard_key
