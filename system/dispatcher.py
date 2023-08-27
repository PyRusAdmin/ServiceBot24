import configparser
import logging

from aiogram import Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher

config = configparser.ConfigParser(empty_lines_in_values=False, allow_no_value=True)
config.read("setting/config.ini")  # Чтение файла
bot_token = config.get('BOT_TOKEN', 'BOT_TOKEN')  # Получение токена
CHANNEL_ID = config.get('CHANNEL_ID', 'CHANNEL_ID')
ADMIN_CHAT_ID = config.get('ADMIN_CHAT_ID', 'ADMIN_CHAT_ID')

bot = Bot(token=bot_token, parse_mode="HTML")
storage = MemoryStorage()  # Хранилище
dp = Dispatcher(bot, storage=storage)
logging.basicConfig(level=logging.INFO)  # Логирования
