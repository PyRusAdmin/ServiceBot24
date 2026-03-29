# -*- coding: utf-8 -*-
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def payment_keyboards() -> InlineKeyboardMarkup:
    """Клавиатура покупки товаров"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='🛒 Купить TelegramMaster-PRO',
                    callback_data='delivery'
                )
            ],
            [
                InlineKeyboardButton(
                    text='🛒 Купить TelegramMaster_Commentator',
                    callback_data='delivery_com'
                )
            ],
            [
                InlineKeyboardButton(
                    text='🛒 Купить TelegramMaster-Search-GPT ',
                    callback_data='delivery_telegrammaster_search_gpt'
                )
            ],
            [
                InlineKeyboardButton(
                    text='🛒 Купить MaxMaster',
                    callback_data='delivery_maxmaster'
                )
            ],
            [
                InlineKeyboardButton(
                    text='🖥️ Аренда сервера',
                    callback_data='delivery_server_rent'
                )
            ],
            [
                InlineKeyboardButton(
                    text='⚙️ Оплатить настройку ПО',
                    callback_data='purchasing_a_program_setup_service'
                )
            ],
            [
                InlineKeyboardButton(
                    text='🏠 В начальное меню',
                    callback_data='start_menu_keyboard'
                )
            ],
        ]

    )


def greeting_keyboards() -> InlineKeyboardMarkup:
    """Клавиатуры поста приветствия 👋(Получения пароля от проектов, обратная связь, отправка логов)"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='🔑 Пароль от TelegramMaster-PRO',
                    callback_data='get_password'
                )
            ],
            [
                InlineKeyboardButton(
                    text='🔑 Пароль от TelegramMaster_Commentator',
                    callback_data='commentator_password'
                )
            ],
            [
                InlineKeyboardButton(
                    text='🛒 Оплата товаров и услуг',
                    callback_data='payment_goods_and_services'
                )
            ],
            [
                InlineKeyboardButton(
                    text='📨 Отправить log файл', callback_data='sending_file'
                ),
                InlineKeyboardButton(
                    text='📱 Мои контакты', callback_data='reference'
                )
            ],
            [
                InlineKeyboardButton(
                    text='⁉️ FAG',
                    callback_data='fag'
                )
            ],
            [
                InlineKeyboardButton(
                    text='💡 Предложить улучшение',
                    callback_data='wish'
                )
            ],
            [
                InlineKeyboardButton(
                    text='Личный кабинет',
                    callback_data='user_account'
                )
            ],
        ]
    )


def user_account_keyboard():
    """
     Личные данные пользователя

    :return: клавиатуру с личными данными юзера.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Мои заказы', callback_data='my_orders')],
            [InlineKeyboardButton(text='🏠 В начальное меню', callback_data='start_menu_keyboard')],
        ]
    )


def start_menu() -> InlineKeyboardMarkup:
    """Клавиатура начального меню"""
    rows = [
        [InlineKeyboardButton(text='🏠 В начальное меню', callback_data='start_menu_keyboard')],
    ]
    inline_keyboard_markup = InlineKeyboardMarkup(inline_keyboard=rows)

    return inline_keyboard_markup


if __name__ == '__main__':
    greeting_keyboards()
