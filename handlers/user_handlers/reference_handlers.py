from aiogram import F
from aiogram import types

from keyboards.user_keyboards import start_menu
from messages.user_messages import message_text_faq  # Пояснение для пользователя FAG
from system.dispatcher import dp, bot  # Подключение к боту и диспетчеру пользователя


@dp.callback_query(F.data == "reference")
async def faq_handler(callback_query: types.CallbackQuery):
    """Пояснение для пользователя FAG"""
    inline_keyboard_markup = start_menu()  # Отправляемся в главное меню
    await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                message_id=callback_query.message.message_id,
                                text=message_text_faq,
                                reply_markup=inline_keyboard_markup,
                                disable_web_page_preview=True)


def register_faq_handler():
    dp.message.register(faq_handler)
