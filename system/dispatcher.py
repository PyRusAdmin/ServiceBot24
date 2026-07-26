import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

load_dotenv()  # Загружаем переменные окружения из файла .env

CRYPTOMUS_API_KEY = os.getenv('CRYPTOMUS_API_KEY')
CRYPTOMUS_MERCHANT_ID = os.getenv('CRYPTOMUS_MERCHANT_ID')

# Токен бота в Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

# Идентификатор и секретный ключ для Yookassa
ACCOUNT_ID = os.getenv("ACCOUNT_ID")
SECRET_KEY = os.getenv("SECRET_KEY")

api_key = os.getenv("GROQ_API_KEY")

# Установка прокси
USER_PROXY = os.getenv("PROXY_USER")
PASSWORD_PROXY = os.getenv("PROXY_PASSWORD")
PORT_PROXY = os.getenv("PROXY_PORT")
IP_PROXY = os.getenv("PROXY_IP")

storage = MemoryStorage()  # Создаем объект MemoryStorage
dp = Dispatcher(storage=storage)  # Создаем объект Dispatcher

# Используем SOCKS5 прокси через URL (если задан)
if USER_PROXY and PASSWORD_PROXY and PORT_PROXY and IP_PROXY:
    session = AiohttpSession(proxy=f"socks5://{USER_PROXY}:{PASSWORD_PROXY}@{IP_PROXY}:{PORT_PROXY}")
else:
    session = AiohttpSession()

bot = Bot(
    token=TELEGRAM_BOT_TOKEN,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML
    ),  # Устанавливаем parse_mode для HTML
    session=session  # Устанавливаем сессию для бота и прокси
)
