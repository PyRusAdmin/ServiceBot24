from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def greeting_keyboards():
    """Клавиатуры поста приветствия 👋"""
    keyboards_greeting = InlineKeyboardMarkup()
    get_a_bonus = InlineKeyboardButton(text='📥 Получить пароль от Telegram_SMM_BOT', callback_data='get_password')
    reference_keyboard = InlineKeyboardButton(text='📤 Отправить log файл', callback_data='sending_file')  # Контакты
    keyboards_greeting.row(get_a_bonus)
    keyboards_greeting.row(reference_keyboard)
    return keyboards_greeting


if __name__ == '__main__':
    greeting_keyboards()