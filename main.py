import asyncio
import logging
import sys

from loguru import logger  # https://github.com/Delgan/loguru

from handlers.fag_handlers import fag_register_message_handler
from handlers.program_service_handlers import buy_handler_program_setup_service
from handlers.sale_of_goods_handlers import buy_handler
from handlers.user_handlers.user_handlers import greeting_handler
from system.dispatcher import dp, bot

logger.add("logs/log.log", retention="1 days", enqueue=True)  # Логирование бота


async def main() -> None:
    """Запуск бота https://t.me/h24service_bot"""
    await dp.start_polling(bot)
    # buy_handler_program_admin_service()  # Удаление системных сообщений
    greeting_handler()  # Пост приветствие пользователей бота
    buy_handler()  # Купить Telegram_BOT_SMM
    buy_handler_program_setup_service()  # Оплата настройки ПО
    fag_register_message_handler()  # Помощь по боту


if __name__ == '__main__':
    try:
        # main()  # Запуск бота
        logging.basicConfig(level=logging.INFO, stream=sys.stdout)
        asyncio.run(main())
    except Exception as e:
        logger.exception(e)
