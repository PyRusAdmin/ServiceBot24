import sqlite3

from aiogram import F
from aiogram.enums import ChatAction
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery
from groq import AsyncGroq

from setting.proxy_config import setup_proxy
from setting.settings import get_groq_api_key
from system.dispatcher import bot, dp, ADMIN_CHAT_ID




# Инициализация базы данных
def init_db():
    conn = sqlite3.connect('setting/user_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_wishes (
            user_id INTEGER,
            wish TEXT
        )
    ''')
    conn.commit()
    conn.close()


init_db()


def remove_markdown_symbols(text: str) -> str:
    """Удаляет символы Markdown (* и **) из текста."""
    return text.replace("*", "")


class WishState(StatesGroup):
    waiting_for_wish = State()


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
    setup_proxy()  # Установка прокси

    # Инициализация Groq клиента
    client = AsyncGroq(api_key=get_groq_api_key())

    user_id = message.from_user.id
    user_wish = message.text

    # Показываем, что бот "печатает"
    await bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)

    # Формируем запрос к Groq API для обработки пожеланий
    chat_completion = await client.chat.completions.create(
        messages=[{"role": "user",
                   "content": f"""Сформулируй пожелание пользователя для разработчика. Пожелание: "{user_wish}"""}],
        model="mixtral-8x7b-32768",
    )

    # Получаем ответ от ИИ
    ai_response = chat_completion.choices[0].message.content

    # Удаляем символы Markdown (* и **)
    clean_response = remove_markdown_symbols(ai_response)

    # Отправляем обработанное пожелание администратору
    await bot.send_message(chat_id=ADMIN_CHAT_ID,
                           text=f"Пользователь {user_id} оставил пожелание:\n{clean_response}")

    # Сохраняем пожелание в базу данных
    conn = sqlite3.connect('setting/user_data.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO user_wishes (user_id, wish) VALUES (?, ?)', (user_id, clean_response))
    conn.commit()
    conn.close()

    # Отправляем ответ пользователю
    await message.answer("Ваше пожелание было обработано и отправлено администратору. Спасибо!")

    # Сбрасываем состояние
    await state.clear()


def register_ai_handlers():
    dp.callback_query.register(cmd_wish)
    dp.message.register(handle_wish, WishState.waiting_for_wish)
