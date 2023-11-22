from aiogram import executor
from loguru import logger

from handlers.fag_handlers import fag_register_message_handler
from handlers.program_service_handlers import buy_handler_program_setup_service
from handlers.sale_of_goods_handlers import buy_handler
from handlers.user_handlers import greeting_handler
from system.dispatcher import dp

logger.add("logs/log.log", retention="1 days", enqueue=True)  # Логирование бота


def main() -> None:
    """Запуск бота https://t.me/h24service_bot"""
    executor.start_polling(dp, skip_updates=True)
    greeting_handler()
    buy_handler()  # Купить Telegram_BOT_SMM
    buy_handler_program_setup_service()  # Оплата настройки ПО
    fag_register_message_handler()  # Помощь по боту


if __name__ == '__main__':
    try:
        main()  # Запуск бота
    except Exception as e:
        logger.exception(e)
