import datetime  # Дата
import sqlite3

from aiogram import F
from aiogram import types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import FSInputFile
from loguru import logger

from keyboards.user_keyboards import greeting_keyboards  # Клавиатуры поста приветствия
from messages.user_messages import greeting_post  # Пояснение для пользователя FAG
from system.dispatcher import dp, bot, ADMIN_CHAT_ID  # Подключение к боту и диспетчеру пользователя


class SomeState(StatesGroup):
    some_state = State()  # Пример состояния, можно добавить дополнительные состояния


@dp.message(Command('start'))
async def greeting(message: types.Message, state: FSMContext):
    """Обработчик команды /start, он же пост приветствия"""
    await state.clear()
    # await state.reset_state()
    # Получаем текущую дату и время
    current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Записываем данные пользователя в базу данных
    # Инициализация базы данных SQLite
    conn = sqlite3.connect('setting/user_data.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users_run (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, 
                                                        first_name TEXT, last_name TEXT, username TEXT, date TEXT)''')
    cursor.execute('''INSERT INTO users_run (user_id, first_name, last_name, username, date) VALUES (?, ?, ?, ?, ?)''',
                   (message.from_user.id, message.from_user.first_name, message.from_user.last_name,
                    message.from_user.username, current_date))
    conn.commit()
    print(f'Запустили бота: {message.from_user.id, message.from_user.username, current_date}')
    keyboards_greeting = greeting_keyboards()
    # Клавиатура для Калькулятора цен или Контактов
    await message.answer(
        text=greeting_post,
        reply_markup=keyboards_greeting,
        disable_web_page_preview=True,
        parse_mode="HTML"
    )


@dp.callback_query(F.data == 'start_menu')
async def start_menu(callback_query: types.CallbackQuery, state: FSMContext):
    """Обработчик команды /start, он же пост приветствия"""
    await state.clear()
    current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Получаем текущую дату и время
    # Записываем данные пользователя в базу данных
    # Инициализация базы данных SQLite
    conn = sqlite3.connect('setting/user_data.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users_run (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, 
                                                        first_name TEXT, last_name TEXT, username TEXT, date TEXT)''')
    cursor.execute('''INSERT INTO users_run (user_id, first_name, last_name, username, date) VALUES (?, ?, ?, ?, ?)''',
                   (
                       callback_query.from_user.id, callback_query.from_user.first_name,
                       callback_query.from_user.last_name,
                       callback_query.from_user.username, current_date))
    conn.commit()
    logger.info(f'Запустили бота: {callback_query.from_user.id, callback_query.from_user.username, current_date}')
    keyboards_greeting = greeting_keyboards()
    # Клавиатура для Калькулятора цен или Контактов
    await bot.edit_message_text(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        text=greeting_post,
        reply_markup=keyboards_greeting,
        disable_web_page_preview=True,
        parse_mode="HTML",
    )


@dp.callback_query(F.data == 'start_menu_keyboard')
async def start_menu_no_edit(callback_query: types.CallbackQuery, state: FSMContext):
    """Обработчик команды /start, он же пост приветствия"""
    await state.clear()
    current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Получаем текущую дату и время
    # Записываем данные пользователя в базу данных
    # Инициализация базы данных SQLite
    conn = sqlite3.connect('setting/user_data.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users_run (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, 
                                                        first_name TEXT, last_name TEXT, username TEXT, date TEXT)''')
    cursor.execute('''INSERT INTO users_run (user_id, first_name, last_name, username, date) VALUES (?, ?, ?, ?, ?)''',
                   (
                       callback_query.from_user.id, callback_query.from_user.first_name,
                       callback_query.from_user.last_name,
                       callback_query.from_user.username, current_date))
    conn.commit()
    logger.info(f'Запустили бота: {callback_query.from_user.id, callback_query.from_user.username, current_date}')
    keyboards_greeting = greeting_keyboards()
    await bot.send_message(callback_query.message.chat.id, greeting_post, reply_markup=keyboards_greeting,
                           parse_mode="HTML", )


def checking_for_presence_in_the_user_database(user_id):
    # Инициализация базы данных SQLite
    conn = sqlite3.connect('setting/user_data.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY)')
    # Проверка наличия ID в базе данных
    cursor.execute('SELECT id FROM users WHERE id = ?', (user_id,))
    result = cursor.fetchone()
    return result


# Инициализация базы данных SQLite
conn = sqlite3.connect('setting/user_data.db')
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY)')


@dp.message(Command('id'))
async def process_id_command(message: types.Message):
    """Обработчик команды /id"""
    try:
        user_id = int(message.text.split()[1])
        result = checking_for_presence_in_the_user_database(user_id)  # Запись ID в базу данных
        if result is None:
            cursor.execute('INSERT INTO users (id) VALUES (?)', (user_id,))
            conn.commit()
            await message.reply(f"ID {user_id} успешно записан в базу данных.")
        else:
            await message.reply(f"ID {user_id} уже существует в базе данных.")
    except (IndexError, ValueError):
        await message.reply("Используйте команду /id followed by ваш ID.")
    except Exception as error:
        logger.exception(error)


@dp.callback_query(F.data == "get_password_tg_com")
async def get_password_tg_com(callback: types.CallbackQuery):
    """Проверка подписки на канал, бот обязательно должен быть админом, ссылка в виде: @master_tg_d"""
    logger.info(f'Пользователь {callback.from_user.id} {callback.from_user.username} запросил / запросила пароль '
                f'от Telegram_Commentator_GPT')
    # Проверьте статус подписки пользователя
    user = await bot.get_chat_member(chat_id="@master_tg_d", user_id=callback.from_user.id)
    if user.status in ['member', 'administrator', 'creator']:
        document = FSInputFile('setting/password/Telegram_Commentator_GPT/password.txt')
        await bot.send_document(chat_id=callback.message.chat.id, document=document)
        await bot.send_message(chat_id=ADMIN_CHAT_ID, text=f"Пользователь:\n"
                                                           f"ID {callback.from_user.id},\n"
                                                           f"Username: @{callback.from_user.username},\n"
                                                           f"Имя: {callback.from_user.first_name},\n"
                                                           f"Фамилия: {callback.from_user.last_name},\n"
                                                           f"Запросил пароль от Telegram_Commentator_GPT")
    else:
        # Пользователь не подписан, отправьте сообщение с просьбой подписаться.
        await bot.send_message(callback.message.chat.id,
                               "Пожалуйста, подпишитесь на канал @master_tg_d и попробуйте снова.")
        await bot.send_message(chat_id=ADMIN_CHAT_ID, text=f"Пользователь:\n"
                                                           f"ID {callback.from_user.id},\n"
                                                           f"Username: @{callback.from_user.username},\n"
                                                           f"Имя: {callback.from_user.first_name},\n"
                                                           f"Фамилия: {callback.from_user.last_name},\n"
                                                           f"Запросил пароль от Telegram_Commentator_GPT")


def greeting_handler():
    dp.message.register(greeting)
    # dp.message.register(get_password)
    dp.message.register(process_id_command)
    dp.message.register(start_menu)
