from aiogram import types, F

from keyboards.user_keyboards import start_menu
from messages.messages import fag_post
from system.dispatcher import bot, dp


@dp.callback_query(F.data == "fag")
async def fag_handler(callback_query: types.CallbackQuery):
    inline_keyboard_markup = start_menu()  # Отправляемся в главное меню
    await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                message_id=callback_query.message.message_id,
                                text=fag_post,
                                reply_markup=inline_keyboard_markup,
                                parse_mode="HTML")


def fag_register_message_handler():
    """Регистрируем handlers для бота"""
    dp.message.register(fag_handler)
