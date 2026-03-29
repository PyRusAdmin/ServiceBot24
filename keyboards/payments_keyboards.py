# -*- coding: utf-8 -*-
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def payment_keyboard_telegram_master_search_gpt(payment_id) -> InlineKeyboardMarkup:
    """Создает клавиатуру для оплаты TelegramMaster-Search-GPT и возврата в главное меню"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='✅ Проверить оплату (Yookassa)', callback_data=f"CheckPayTMSearchGPT_{payment_id}")],
        [InlineKeyboardButton(text='🏠 В начальное меню', callback_data='start_menu_keyboard')],
    ])


def payment_yookassa_password_commentator_password_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура оплаты пароля TelegramMaster_Commentator"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=f"💳 Оплатить Yookassa",
                                 callback_data='payment_yookassa_password_commentator_password'),
            InlineKeyboardButton(text="⭐️ Оплатить Stars", callback_data='payment_stars_commentator_password'),
        ],
        [InlineKeyboardButton(text='🏠 В начальное меню', callback_data='start_menu_keyboard')],
    ]
    )


def payment_keyboard_telegram_master_search_gpt_1() -> InlineKeyboardMarkup:
    """Клавиатура оплаты TelegramMaster_Search_GPT"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💳 Оплатить Yookassa", callback_data='payment_yookassa_Search_GPT'),
            InlineKeyboardButton(text="⭐️ Оплатить Stars", callback_data='payment_stars_search_gpt'),
        ],
        [InlineKeyboardButton(text='🏠 В начальное меню', callback_data='start_menu_keyboard')],
    ]
    )


def payment_keyboard_password() -> InlineKeyboardMarkup:
    """Клавиатура оплаты пароля TelegramMaster"""
    rows = [
        [
            InlineKeyboardButton(text=f"💳 Оплатить YooKassa (все методы)", callback_data='payment_yookassa_password'),
            InlineKeyboardButton(text="⭐️ Оплатить Stars", callback_data='payment_stars_password'),
        ],
        [
            InlineKeyboardButton(text="⚡ СБП (быстрые платежи)", callback_data='payment_yookassa_password_sbp'),
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
            InlineKeyboardButton(text="⭐️ Оплатить Stars", callback_data='payment_stars_training'),
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
            InlineKeyboardButton(text="⭐️ Оплатить Stars", callback_data='payment_stars_commentator'),
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
            InlineKeyboardButton(text="⭐️ Оплатить Stars", callback_data='payment_stars_program'),
        ],
        [InlineKeyboardButton(text='🏠 В начальное меню', callback_data='start_menu_keyboard')],
    ]
    payment_keyboard_key = InlineKeyboardMarkup(inline_keyboard=rows)
    return payment_keyboard_key


def payment_keyboard_maxmaster() -> InlineKeyboardMarkup:
    """Клавиатура оплаты MaxMaster"""
    rows = [
        [
            InlineKeyboardButton(text="💳 Оплатить Yookassa", callback_data='payment_yookassa_maxmaster'),
            InlineKeyboardButton(text="⭐️ Оплатить Stars", callback_data='payment_stars_maxmaster'),
        ],
        [InlineKeyboardButton(text='🏠 В начальное меню', callback_data='start_menu_keyboard')],
    ]
    payment_keyboard_key = InlineKeyboardMarkup(inline_keyboard=rows)
    return payment_keyboard_key


def payment_keyboard_server_rent() -> InlineKeyboardMarkup:
    """Клавиатура оплаты аренды сервера"""
    rows = [
        [
            InlineKeyboardButton(text="💳 Оплатить Yookassa", callback_data='payment_yookassa_server_rent'),
            InlineKeyboardButton(text="⭐️ Оплатить Stars", callback_data='payment_stars_server_rent'),
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
    payment_keyboard_maxmaster()
    payment_keyboard_server_rent()
