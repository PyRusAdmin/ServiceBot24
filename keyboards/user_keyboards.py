from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def payment_keyboard(url, id_pay) -> InlineKeyboardBuilder:
    """Клавиатура оплаты"""
    payment_keyboard_key = InlineKeyboardBuilder()
    payment_keyboard_key.add(InlineKeyboardButton(text="💳 Оплатить 1000 руб.", url=url))
    payment_keyboard_key.add(InlineKeyboardButton(text='Проверить оплату', callback_data=f"check_payment_{id_pay}"))
    return payment_keyboard_key


def greeting_keyboards():
    """Клавиатуры поста приветствия 👋(Получения пароля от проектов, обратная связь, отправка логов)"""

    rows = [
        [InlineKeyboardButton(text='📥 Пароль от TelegramMaster', callback_data='get_password')],
        [InlineKeyboardButton(text='📤 Пароль от Telegram_Commentator_GPT', callback_data='get_password_tg_com')],
        [InlineKeyboardButton(text='Купить TelegramMaster', callback_data='delivery')],
        [InlineKeyboardButton(text='Оплатить настройку ПО', callback_data='purchasing_a_program_setup_service')],
        [
            InlineKeyboardButton(text='📨 Отправить log файл', callback_data='sending_file'),
            InlineKeyboardButton(text='📱 Мои контакты', callback_data='reference')
        ],
        [InlineKeyboardButton(text='⁉️ FAG', callback_data='fag')],
    ]
    inline_keyboard_markup = InlineKeyboardMarkup(inline_keyboard=rows)

    return inline_keyboard_markup


if __name__ == '__main__':
    greeting_keyboards()
