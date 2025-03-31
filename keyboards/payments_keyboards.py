# -*- coding: utf-8 -*-
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def payment_yookassa_password_commentator_password_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура оплаты пароля TelegramMaster_Commentator"""
    rows = [
        [
            InlineKeyboardButton(text=f"💳 Оплатить Yookassa",
                                 callback_data='payment_yookassa_password_commentator_password'),
            InlineKeyboardButton(text=f"💳 Оплатить (Крипта)", callback_data=f"payment_crypta_commentator_pass")
        ],
        [InlineKeyboardButton(text='🏠 В начальное меню', callback_data='start_menu_keyboard')],
    ]
    payment_keyboard_password_key = InlineKeyboardMarkup(inline_keyboard=rows)
    return payment_keyboard_password_key


def payment_keyboard_password() -> InlineKeyboardMarkup:
    """Клавиатура оплаты пароля TelegramMaster"""
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


def payment_keyboard_com() -> InlineKeyboardMarkup:
    """Клавиатура оплаты TelegramMaster_Commentator"""
    rows = [
        [
            InlineKeyboardButton(text="💳 Оплатить Yookassa", callback_data='payment_yookassa_commentator'),
            InlineKeyboardButton(text="💳 Оплатить (Крипта)", callback_data="payment_crypta_commentator"),
        ],
        [InlineKeyboardButton(text='🏠 В начальное меню', callback_data='start_menu_keyboard')],
    ]
    payment_keyboard_key = InlineKeyboardMarkup(inline_keyboard=rows)
    return payment_keyboard_key


def payment_keyboard_telegram_master_search_gpt() -> InlineKeyboardMarkup:
    """Клавиатура оплаты TelegramMaster_Search_GPT"""
    rows = [
        [
            InlineKeyboardButton(text="💳 Оплатить Yookassa", callback_data='payment_yookassa_Search_GPT'),
            InlineKeyboardButton(text="💳 Оплатить (Крипта)", callback_data="payment_crypta_Search_GPT"),
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


if __name__ == '__main__':
    payment_keyboard_com()
    payment_keyboard()
    purchasing_a_program_setup_service()
    payment_keyboard_password()
    payment_yookassa_password_commentator_password_keyboard()
