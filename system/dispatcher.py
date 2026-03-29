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
PROXY_USER = get_proxy_user()
PROXY_PASSWORD = get_proxy_password()
PROXY_PORT = get_proxy_port()
PROXY_IP = get_proxy_ip()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

bot = Bot(
    token=TELEGRAM_BOT_TOKEN,
)

storage = MemoryStorage()  # Хранилище
dp = Dispatcher(storage=storage)
logging.basicConfig(level=logging.INFO)  # Логирования

form_router = Router()
dp.include_router(form_router)
