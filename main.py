import asyncio
import logging

from loguru import logger  # https://github.com/Delgan/loguru

from handlers.payments.cryptomus_payments.password_handlers import cry_register_message_handler
from handlers.payments.cryptomus_payments.program_handlers import program_cry_register_message_handler
from handlers.payments.cryptomus_payments.training_handlers import training_cry_register_message_handler
from handlers.user.fag_handlers import fag_register_message_handler
from handlers.user.reference_handlers import register_faq_handler
from handlers.user.sending_log_file import sending_log_file_register_handler
from handlers.user.user_handlers import greeting_handler
from handlers.payments.yookassa_payments.program_service_handlers import buy_handler_program_setup_service
from handlers.payments.yookassa_payments.sale_of_goods_handlers import buy_handler
from system.dispatcher import dp, bot

logger.add("logs/log.log", rotation="1 MB", compression="zip", level="INFO")  # Логирование программы
logger.add("logs/log_ERROR.log", rotation="1 MB", compression="zip", level="ERROR")  # Логирование программы


async def main() -> None:
    """Запуск бота https://t.me/h24service_bot"""
    await dp.start_polling(bot)
    # buy_handler_program_admin_service()  # Удаление системных сообщений

    # Рабата с пользователем бота
    greeting_handler()  # Пост приветствие пользователей бота
    fag_register_message_handler()  # Помощь по боту
    sending_log_file_register_handler()  # Отправка логов боту
    register_faq_handler()  # Регистрация FAQ

    # Оплата Юкасса
    buy_handler()  # Купить TelegramMaster 2.0
    buy_handler_program_setup_service()  # Оплата настройки ПО

    # Оплата Криптой
    cry_register_message_handler()  # Покупка пароля TelegramMaster 2.0
    program_cry_register_message_handler()  # Покупка TelegramMaster 2.0
    training_cry_register_message_handler()  # Покупка 'Помощь в настройке ПО (консультация)'


if __name__ == '__main__':
    try:
        logging.basicConfig()
        asyncio.run(main())
    except Exception as e:
        logger.exception(e)
