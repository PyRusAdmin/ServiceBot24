import datetime  # Дата
import sqlite3
from loguru import logger
from aiogram import types
from aiogram.dispatcher import FSMContext  # Состояния пользователя
from aiogram.dispatcher.filters.state import State, StatesGroup

from keyboards.user_keyboards import greeting_keyboards  # Клавиатуры поста приветствия
from messages.user_messages import greeting_post, message_text_faq  # Пояснение для пользователя FAG
from system.dispatcher import dp, bot, CHANNEL_ID, ADMIN_CHAT_ID  # Подключение к боту и диспетчеру пользователя


class SomeState(StatesGroup):
    some_state = State()  # Пример состояния, можно добавить дополнительные состояния


@dp.message_handler(commands=['start'])
async def greeting(message: types.Message, state: FSMContext):
    """Обработчик команды /start, он же пост приветствия"""
    await state.finish()
    await state.reset_state()
    # Получаем текущую дату и время
    current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Записываем данные пользователя в базу данных
    # Инициализация базы данных SQLite
    conn = sqlite3.connect('setting/user_data.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users_run (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, 
                                                        first_name TEXT, last_name TEXT, username TEXT, date TEXT)''')
    cursor.execute('''INSERT INTO users_run (user_id, first_name, last_name, username, date) VALUES (?, ?, ?, ?, ?)''',
                   (
                       message.from_user.id, message.from_user.first_name, message.from_user.last_name,
                       message.from_user.username,
                       current_date))
    conn.commit()
    print(f'Запустили бота: {message.from_user.id, message.from_user.username, current_date}')
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
    print(f"User Status: {user.status}")
    if user.status == "member" or user.status == "administrator" or user.status == "creator":
        # Проверка наличия ID в базе данных
        cursor.execute('SELECT id FROM users WHERE id = ?', (user_id,))
        result = cursor.fetchone()
        if result:
            # Пользователь подписан и имеет ID в базе данных, отправляем файл с паролем
            # Замените 'password.txt' на путь к файлу с паролем
            with open('setting/password/Telegram_SMM_BOT/password.txt', 'rb') as password_file:
                await bot.send_document(chat_id, password_file)
        else:
            # Пользователь не имеет ID в базе данных
            await bot.send_message(chat_id,
                                   "Вы должны быть зарегистрированы и подписаны на канал @bot_telegram_SMM_help.")
    else:
        # Пользователь не подписан, отправляем сообщение с просьбой подписаться
        await bot.send_message(chat_id, "Пожалуйста, подпишитесь на канал @bot_telegram_SMM_help и попробуйте снова.")


@dp.callback_query_handler(text='get_password_tg_com')
async def get_password_tg_com(callback_query: types.CallbackQuery):
    """Проверка подписки на канал, бот обязательно должен быть админом"""
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id

    # Проверьте статус подписки пользователя
    user = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
    print(f"User Status: {user.status}")

    if user.status == "member" or user.status == "administrator" or user.status == "creator":
        # Пользователь подписан, отправьте файл паролей
        with open('setting/password/Telegram_Commentator_GPT/password.txt', 'rb') as password_file:
            await bot.send_document(chat_id, password_file)
    else:
        # Пользователь не подписан, отправьте сообщение с просьбой подписаться.
        await bot.send_message(chat_id, "Пожалуйста, подпишитесь на канал @bot_telegram_SMM_help и попробуйте снова.")


# Инициализация базы данных SQLite
conn = sqlite3.connect('setting/user_data.db')
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY)')


@dp.message_handler(commands=['id'])
async def process_id_command(message: types.Message):
    """Обработчик команды /id"""
    try:
        user_id = int(message.text.split()[1])
        # Запись ID в базу данных
        cursor.execute('SELECT id FROM users WHERE id = ?', (user_id,))
        result = cursor.fetchone()
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


@dp.callback_query_handler(lambda c: c.data.startswith('sending_file'))
async def sending_file_callback(callback_query: types.CallbackQuery):
    """Обработчик коллбэков для кнопки "sending_file"""
    # user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id
    # Получение ID файла из данных коллбэка (пока кнопка не привязана к конкретному файлу)
    # Отправляем сообщение с просьбой отправить файл
    await bot.send_message(chat_id, "Пожалуйста, отправьте файл, который вы хотите отправить администратору.")
    # Устанавливаем состояние, ожидая файла от пользователя
    await SomeState.some_state.set()


@dp.message_handler(state=SomeState.some_state, content_types=['document', 'photo', 'video'])
async def handle_sending_file(message: types.Message, state: FSMContext):
    """Обработчик отправки файла в состоянии "some_state"""
    # Получаем ID пользователя и файловой ID
    user_id = message.from_user.id
    file_id = None
    if message.document:
        file_id = message.document.file_id
    elif message.photo:
        file_id = message.photo[-1].file_id
    elif message.video:
        file_id = message.video.file_id
    if file_id:
        # Отправка файла администратору по его file_id
        admin_chat_id = ADMIN_CHAT_ID  # Замените на ID чата администратора
        await bot.send_document(admin_chat_id, document=file_id)
        # Очищаем состояние
        await state.finish()
        await message.reply("Ваш файл успешно отправлен администратору.")


@dp.callback_query_handler(lambda c: c.data == 'reference')
async def faq_handler(callback_query: types.CallbackQuery):
    """Пояснение для пользователя FAG"""
    # disable_web_page_preview=True - скрыть предпросмотр ссылок в Telegram
    await bot.send_message(callback_query.from_user.id, message_text_faq, disable_web_page_preview=True,
                           parse_mode=types.ParseMode.HTML)


def greeting_handler():
    """Регистрируем handlers для бота"""
    dp.register_message_handler(greeting)  # Обработчик команды /start, он же пост приветствия
    dp.register_message_handler(handle_sending_file)  # Обработчик команды /start, он же пост приветствия
