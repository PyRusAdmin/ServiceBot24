import datetime  # Дата
import sqlite3

from aiogram import F
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.filters import StateFilter
from aiogram.fsm import state
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import FSInputFile
from loguru import logger

from keyboards.user_keyboards import greeting_keyboards  # Клавиатуры поста приветствия
from messages.user_messages import greeting_post, message_text_faq  # Пояснение для пользователя FAG
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
        # parse_mode=types.ParseMode.HTML
    )


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
        # Запись ID в базу данных
        result = checking_for_presence_in_the_user_database(user_id)
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


@dp.callback_query(F.data == "get_password")
async def get_password(callback: types.CallbackQuery):
    """Обработчик команды /get_password для получения пароля для пользователя"""
    try:
        logger.info(f'Пользователь {callback.from_user.id} {callback.from_user.username} запросил / запросила пароль '
                    f'от TelegramMaster')
        logger.info(callback.from_user.id)  # Проверка ID пользователя
        user = await bot.get_chat_member(chat_id="@master_tg_d", user_id=callback.from_user.id)  # Проверка подписки
        logger.info(f"User Status: {user.status}")
        if user.status in ['member', 'administrator', 'creator']:
            result = checking_for_presence_in_the_user_database(callback.from_user.id)
            if result:
                # Пользователь подписан и имеет ID в базе данных, отправляем файл с паролем
                document = FSInputFile('setting/password/Telegram_SMM_BOT/password.txt')
                await bot.send_document(chat_id=callback.message.chat.id, document=document)
                await bot.send_message(chat_id=ADMIN_CHAT_ID, text=f"Пользователь:\n"
                                                                   f"ID {callback.from_user.id},\n"
                                                                   f"Username: @{callback.from_user.username},\n"
                                                                   f"Имя: {callback.from_user.first_name},\n"
                                                                   f"Фамилия: {callback.from_user.last_name},\n"
                                                                   f"Запросил пароль от TelegramMaster")  # ID пользователя нет в базе данных
            else:
                text = (
                    "Для того чтобы воспользоваться всеми возможностями бота 🤖, вам необходимо подписаться на канал "
                    "🔗 @master_tg_d и купить TelegramMaster.\n\n"

                    "Это позволит вам получить самую свежую версию TelegramMaster и воспользоваться всеми новыми "
                    "функциями.\n\n"

                    "Если вы ранее уже приобретали TelegramMaster, но бот 🤖 не выдаёт пароль, обратитесь к "
                    "🔗 @h24service_bot.")
                await bot.send_message(chat_id=callback.message.chat.id, text=text)  # ID пользователя нет в базе данных
                await bot.send_message(chat_id=ADMIN_CHAT_ID, text=f"Пользователь:\n"
                                                                   f"ID {callback.from_user.id},\n"
                                                                   f"Username: @{callback.from_user.username},\n"
                                                                   f"Имя: {callback.from_user.first_name},\n"
                                                                   f"Фамилия: {callback.from_user.last_name},\n"
                                                                   f"Запросил пароль от TelegramMaster")  # ID пользователя нет в базе данных
        else:
            text = ("Для того чтобы воспользоваться всеми возможностями бота 🤖, вам необходимо подписаться на канал "
                    "🔗 @master_tg_d и купить TelegramMaster.\n\n"

                    "Это позволит вам получить самую свежую версию TelegramMaster и воспользоваться всеми новыми "
                    "функциями.\n\n"

                    "Если вы ранее уже приобретали TelegramMaster, но бот 🤖 не выдаёт пароль, обратитесь к "
                    "🔗 @h24service_bot.")
            await bot.send_message(chat_id=callback.message.chat.id, text=text)  # ID пользователя нет в базе данных
            await bot.send_message(chat_id=ADMIN_CHAT_ID, text=f"Пользователь:\n"
                                                                   f"ID {callback.from_user.id},\n"
                                                                   f"Username: @{callback.from_user.username},\n"
                                                                   f"Имя: {callback.from_user.first_name},\n"
                                                                   f"Фамилия: {callback.from_user.last_name},\n"
                                                                   f"Запросил пароль от TelegramMaster")   # ID пользователя нет в базе данных
    except Exception as e:
        logger.error(e)


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
                                                           f"Запросил пароль от Telegram_Commentator_GPT")  # ID пользователя нет в базе данных
    else:
        # Пользователь не подписан, отправьте сообщение с просьбой подписаться.
        await bot.send_message(callback.message.chat.id, "Пожалуйста, подпишитесь на канал @master_tg_d и попробуйте снова.")
        await bot.send_message(chat_id=ADMIN_CHAT_ID, text=f"Пользователь:\n"
                                                           f"ID {callback.from_user.id},\n"
                                                           f"Username: @{callback.from_user.username},\n"
                                                           f"Имя: {callback.from_user.first_name},\n"
                                                           f"Фамилия: {callback.from_user.last_name},\n"
                                                           f"Запросил пароль от Telegram_Commentator_GPT")  # ID пользователя нет в базе данных


@dp.callback_query(F.data == "sending_file")
async def sending_file_callback(callback_query: types.CallbackQuery):
    """Обработчик коллбэков для кнопки "sending_file"""
    # user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id
    # Получение ID файла из данных коллбэка (пока кнопка не привязана к конкретному файлу)
    # Отправляем сообщение с просьбой отправить файл
    await bot.send_message(chat_id, "Пожалуйста, отправьте файл, который вы хотите отправить администратору.")
    # Устанавливаем состояние, ожидая файла от пользователя
    await state.set_state(SomeState.some_state)


router = Router()


@router.message(StateFilter(SomeState.some_state), F.photo, F.document, F.video)
async def handle_file(message: types.Message, state: FSMContext):
    """Обработчик отправки файла в состоянии "some_state"""
    # Получаем ID пользователя и файловой ID
    # user_id = message.from_user.id
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
        await state.clear()
        await message.reply("Ваш файл успешно отправлен администратору.")


@dp.callback_query(F.data == "reference")
async def faq_handler(callback_query: types.CallbackQuery):
    """Пояснение для пользователя FAG"""
    # disable_web_page_preview=True - скрыть предпросмотр ссылок в Telegram
    await bot.send_message(callback_query.from_user.id, message_text_faq, disable_web_page_preview=True)


def greeting_handler():
    dp.message.register(greeting)
    dp.message.register(get_password)
    dp.message.register(process_id_command)
