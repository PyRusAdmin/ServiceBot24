import configparser
import logging

from aiogram import Bot, Dispatcher, Router
from aiogram.fsm.storage.memory import MemoryStorage

config = configparser.ConfigParser(empty_lines_in_values=False, allow_no_value=True)
config.read("setting/config.ini")  # Чтение файла
bot_token = config.get('BOT_TOKEN', 'BOT_TOKEN')  # Получение токена

# Telegram
CHANNEL_ID = config.get('CHANNEL_ID', 'CHANNEL_ID')
ADMIN_CHAT_ID = config.get('ADMIN_CHAT_ID', 'ADMIN_CHAT_ID')

# Юкасса
ACCOUNT_ID = config.get('ACCOUNT_ID', 'ACCOUNT_ID')
SECRET_KEY = config.get('SECRET_KEY', 'SECRET_KEY')

# Крипта
API_KEY = config.get('API_KEY', 'API_KEY')
ID_MERCH = config.get('ID_MERCH', 'ID_MERCH')

bot = Bot(
    token=bot_token,
)
storage = MemoryStorage()  # Хранилище
dp = Dispatcher(storage=storage)
logging.basicConfig(level=logging.INFO)  # Логирования

form_router = Router()
dp.include_router(form_router)
