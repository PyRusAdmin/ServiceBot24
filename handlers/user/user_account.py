# -*- coding: utf-8 -*-
from aiogram import types, F

from keyboards.user_keyboards import start_menu
from system.dispatcher import bot, dp


@dp.callback_query(F.data == "user_account")
async def user_account_handlers(callback_query: types.CallbackQuery):
    """Кабинет пользователя"""

    message_text = (
        f"👋 Привет, <b>{callback_query.from_user.first_name}</b>!\n\n"
        "🔐 Ты вошёл в свой персональный кабинет — закрытую зону доступа, "
        "доступную только тебе.\n\n"
        "📦 Здесь ты можешь:\n"
        "   • Посмотреть свои покупки\n"
        "   • Управлять подписками\n"
        "   • Получить помощь и поддержку\n\n"
        "Спасибо, что пользуешься моими сервисами! 🙌"
    )

    await bot.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        text=message_text,
        reply_markup=start_menu(),  # Клавиатура главного меню
        disable_web_page_preview=True,
        parse_mode='HTML'
    )


def register_user_account_handlers():
    dp.message.register(user_account_handlers)
