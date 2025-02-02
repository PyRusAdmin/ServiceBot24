from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def payment_keyboard_password() -> InlineKeyboardMarkup:
    """Клавиатура оплаты пароля"""
    rows = [
        [
            InlineKeyboardButton(text=f"💳 Оплатить Yookassa", callback_data='payment_yookassa_password'),
            InlineKeyboardButton(text=f"💳 Оплатить (Крипта)", callback_data=f"payment_crypta_pas")
        ],
        [InlineKeyboardButton(text='🏠 В начальное меню', callback_data='start_menu_keyboard')],
    ]
    payment_keyboard_password_key = InlineKeyboardMarkup(inline_keyboard=rows)
    return payment_keyboard_password_key


def purchasing_a_program_setup_service() -> InlineKeyboardMarkup:
    """Клавиатура оплаты за настройку программного обеспечения"""
    rows = [
        [
            InlineKeyboardButton(text=f"💳 Оплатить Yookassa", callback_data='payment_yookassa_training'),
            InlineKeyboardButton(text=f"💳 Оплатить (Крипта)", callback_data=f"payment_crypta_pas_training_handler")
        ],
        [InlineKeyboardButton(text='🏠 В начальное меню', callback_data='start_menu_keyboard')],
    ]
    payment_keyboard_key = InlineKeyboardMarkup(inline_keyboard=rows)
    return payment_keyboard_key


def payment_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура оплаты TelegramMaster"""
    rows = [
        [
            InlineKeyboardButton(text=f"💳 Оплатить Yookassa", callback_data='payment_yookassa_program'),
            InlineKeyboardButton(text=f"💳 Оплатить (Крипта)", callback_data=f"payment_crypta_pas_program"),
        ],
        [InlineKeyboardButton(text='🏠 В начальное меню', callback_data='start_menu_keyboard')],
    ]
    payment_keyboard_key = InlineKeyboardMarkup(inline_keyboard=rows)
    return payment_keyboard_key
