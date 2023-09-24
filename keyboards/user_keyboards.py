from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def greeting_keyboards() -> InlineKeyboardMarkup:
    """Клавиатуры поста приветствия 👋(Получения пароля от проектов, обратная связь, отправка логов)"""
    keyboards_greeting = InlineKeyboardMarkup()
    get_a_bonus = InlineKeyboardButton(text='📥 Получить пароль от Telegram_SMM_BOT',
                                       callback_data='get_password')  # Пароль от Telegram_SMM_BOT
    reference_keyboard = InlineKeyboardButton(text='📤 Отправить log файл',
                                              callback_data='sending_file')  # Контакты
    get_a_bonus_tg_com = InlineKeyboardButton(text='📤 Получить пароль от Telegram_Commentator_GPT',
                                              callback_data='get_password_tg_com')  # Пароль от Telegram_Commentator_GPT
    keyboards_greeting.row(get_a_bonus)
    keyboards_greeting.row(get_a_bonus_tg_com)
    keyboards_greeting.row(reference_keyboard)
    return keyboards_greeting


if __name__ == '__main__':
    greeting_keyboards()
