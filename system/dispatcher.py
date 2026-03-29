# -*- coding: utf-8 -*-
import logging
import os

import environs
from aiogram import Bot, Dispatcher, Router
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
from loguru import logger

load_dotenv()  # Загружаем переменные окружения из файла .env

env = environs.Env()
env.read_env('.env')

CRYPTOMUS_API_KEY = env('CRYPTOMUS_API_KEY')
CRYPTOMUS_MERCHANT_ID = env('CRYPTOMUS_MERCHANT_ID')

# Установка прокси
PROXY_USER = os.getenv("PROXY_USER")
PROXY_PASSWORD = os.getenv("PROXY_PASSWORD")
PROXY_PORT = os.getenv("PROXY_PORT")
PROXY_IP = os.getenv("PROXY_IP")

# Токен бота в Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

# Идентификатор и секретный ключ для Yookassa
ACCOUNT_ID = os.getenv("ACCOUNT_ID")
SECRET_KEY = os.getenv("SECRET_KEY")


api_key = os.getenv("GROQ_API_KEY")



bot = Bot(
    token=TELEGRAM_BOT_TOKEN,
)

storage = MemoryStorage()  # Хранилище
dp = Dispatcher(storage=storage)
logging.basicConfig(level=logging.INFO)  # Логирования

form_router = Router()
dp.include_router(form_router)
