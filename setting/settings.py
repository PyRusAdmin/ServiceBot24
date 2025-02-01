import environs
from loguru import logger
import os
from dotenv import load_dotenv

try:
    env = environs.Env()
    env.read_env('.env')

    CRYPTOMUS_API_KEY = env('CRYPTOMUS_API_KEY')
    CRYPTOMUS_MERCHANT_ID = env('CRYPTOMUS_MERCHANT_ID')
except Exception as e:
    logger.exception(f"Error: {e}")

# Загружаем переменные окружения из файла .env
load_dotenv()


# Функции для получения переменных окружения
def get_groq_api_key() -> str:
    """Возвращает API-ключ для Groq."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY не найден в переменных окружения.")
    return api_key


def get_telegram_bot_token() -> str:
    """Возвращает токен Telegram бота."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN не найден в переменных окружения.")
    return token


# Настройки прокси
def get_proxy_user() -> str:
    """Возвращает логин для прокси."""
    user = os.getenv("USER")
    if not user:
        raise ValueError("USER (логин прокси) не найден в переменных окружения.")
    return user


def get_proxy_password() -> str:
    """Возвращает пароль для прокси."""
    password = os.getenv("PASSWORD")
    if not password:
        raise ValueError("PASSWORD (пароль прокси) не найден в переменных окружения.")
    return password


def get_proxy_port() -> str:
    """Возвращает порт для прокси."""
    port = os.getenv("PORT")
    if not port:
        raise ValueError("PORT (порт прокси) не найден в переменных окружения.")
    return port


def get_proxy_ip() -> str:
    """Возвращает IP для прокси."""
    ip = os.getenv("IP")
    if not ip:
        raise ValueError("IP (адрес прокси) не найден в переменных окружения.")
    return ip


if __name__ == '__main__':
    get_groq_api_key()
    get_telegram_bot_token()
    get_proxy_user()
    get_proxy_password()
    get_proxy_port()
    get_proxy_ip()
