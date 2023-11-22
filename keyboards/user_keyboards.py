from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def greeting_keyboards() -> InlineKeyboardMarkup:
    """Клавиатуры поста приветствия 👋(Получения пароля от проектов, обратная связь, отправка логов)"""
    keyboards_greeting = InlineKeyboardMarkup()
    get_a_bonus = InlineKeyboardButton(text='📥 Пароль от Telegram_SMM_BOT',
                                       callback_data='get_password')  # Пароль от Telegram_SMM_BOT
    get_a_bonus_tg_com = InlineKeyboardButton(text='📤 Пароль от Telegram_Commentator_GPT',
                                              callback_data='get_password_tg_com')  # Пароль от Telegram_Commentator_GPT
    delivery = InlineKeyboardButton(text='Купить Telegram_SMM_BOT', callback_data='delivery')
    payment_for_setup = InlineKeyboardButton(text="Оплатить настройку ПО", callback_data="purchasing_a_program_setup_service")
    reference_keyboard = InlineKeyboardButton(text='📨 Отправить log файл',
                                              callback_data='sending_file')  # Контакты
    feedback_keyboard = InlineKeyboardButton(text="📱 Мои контакты", callback_data="reference")
    fag_keyboard = InlineKeyboardButton(text="⁉️ FAG", callback_data="fag")
    keyboards_greeting.row(get_a_bonus)
    keyboards_greeting.row(get_a_bonus_tg_com)
    keyboards_greeting.row(delivery)
    keyboards_greeting.row(payment_for_setup)
    keyboards_greeting.row(reference_keyboard, feedback_keyboard)
    keyboards_greeting.row(fag_keyboard)
    return keyboards_greeting


if __name__ == '__main__':
    greeting_keyboards()
