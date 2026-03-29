# -*- coding: utf-8 -*-
from aiogram import F
from aiogram.enums import ChatAction
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from groq import AsyncGroq
from aiogram import F, Router, types
from db.settings_db import save_user_wish
from setting.proxy_config import setup_proxy
from states.states import WishState
from system.dispatcher import bot, dp, ADMIN_CHAT_ID, api_key, PROXY_USER, PROXY_PASSWORD, PROXY_IP, PROXY_PORT

router = Router(name=__name__)

def remove_markdown_symbols(text: str) -> str:
    """Удаляет символы Markdown (* и **) из текста."""
    return text.replace("*", "")


@dp.callback_query(F.data.startswith("wish"))
async def cmd_wish(callback_query: CallbackQuery, state: FSMContext):
    """Обработчик команды /wish для запроса пожеланий"""
    await callback_query.answer()
    await callback_query.message.answer(
        "Пожалуйста, напишите ваши пожелания по улучшению программных продуктов или созданию новых продуктов.")
    await state.set_state(WishState.waiting_for_wish)


@dp.message(WishState.waiting_for_wish)
async def handle_wish(message: Message, state: FSMContext):
    """Обработчик текстовых сообщений с пожеланиями"""
    setup_proxy(PROXY_USER, PROXY_PASSWORD, PROXY_IP, PROXY_PORT)  # Установка прокси
    # Инициализация Groq клиента
    client = AsyncGroq(api_key=api_key)
    user_id = message.from_user.id
    user_wish = message.text
    # Показываем, что бот "печатает"
    await bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
    # Формируем запрос к Groq API для обработки пожеланий
    chat_completion = await client.chat.completions.create(
        messages=[{"role": "user",
                   "content": f"""Сформулируй пожелание пользователя для разработчика. Пожелание: "{user_wish}"""}],
        model="meta-llama/llama-4-maverick-17b-128e-instruct",
    )
    # Получаем ответ от ИИ
    ai_response = chat_completion.choices[0].message.content
    # Удаляем символы Markdown (* и **)
    clean_response = remove_markdown_symbols(ai_response)
    # Отправляем обработанное пожелание администратору
    await bot.send_message(chat_id=ADMIN_CHAT_ID,
                           text=f"Пользователь {user_id} оставил пожелание:\n{clean_response}")
    save_user_wish(user_id, clean_response)
    # Отправляем ответ пользователю
    await message.answer("Ваше пожелание было обработано и отправлено администратору. Спасибо!")
    # Сбрасываем состояние
    await state.clear()



