import sqlite3

from aiogram import types
from aiogram.dispatcher import FSMContext  # Состояния пользователя

from keyboards.user_keyboards import greeting_keyboards  # Клавиатуры поста приветствия
from messages.user_messages import greeting_post  # Пояснение для пользователя FAG
from system.dispatcher import dp, bot, CHANNEL_ID  # Подключение к боту и диспетчеру пользователя


@dp.message_handler(commands=['start'])
async def greeting(message: types.Message, state: FSMContext):
    """Обработчик команды /start, он же пост приветствия"""
    await state.finish()
    await state.reset_state()
    keyboards_greeting = greeting_keyboards()
    # Клавиатура для Калькулятора цен или Контактов
    await message.reply(greeting_post, reply_markup=keyboards_greeting, disable_web_page_preview=True,
                        parse_mode=types.ParseMode.HTML)


@dp.callback_query_handler(text='get_password')
async def get_password(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id

    # Проверка подписки на канал
    user = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
    if user.status == "member" or user.status == "administrator":
        # Проверка наличия ID в базе данных
        cursor.execute('SELECT id FROM users WHERE id = ?', (user_id,))
        result = cursor.fetchone()

        if result:
            # Пользователь подписан и имеет ID в базе данных, отправляем файл с паролем
            # Замените 'password.txt' на путь к файлу с паролем
            with open('setting/password.txt', 'rb') as password_file:
                await bot.send_document(chat_id, password_file)
        else:
            # Пользователь не имеет ID в базе данных
            await bot.send_message(chat_id, "Вы должны быть зарегистрированы и подписаны на канал @TG_SMM2.")
    else:
        # Пользователь не подписан, отправляем сообщение с просьбой подписаться
        await bot.send_message(chat_id, "Пожалуйста, подпишитесь на канал @TG_SMM2 и попробуйте снова.")


# Инициализация базы данных SQLite
conn = sqlite3.connect('setting/user_data.db')
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY)')


# Обработчик команды /id
@dp.message_handler(commands=['id'])
async def process_id_command(message: types.Message):
    try:
        user_id = int(message.text.split()[1])

        # Запись ID в базу данных
        cursor.execute('INSERT INTO users (id) VALUES (?)', (user_id,))
        conn.commit()

        await message.reply(f"ID {user_id} успешно записан в базу данных.")
    except (IndexError, ValueError):
        await message.reply("Используйте команду /id followed by ваш ID.")


def greeting_handler():
    """Регистрируем handlers для бота"""
    dp.register_message_handler(greeting)  # Обработчик команды /start, он же пост приветствия
