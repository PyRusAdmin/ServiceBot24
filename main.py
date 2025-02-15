# -*- coding: utf-8 -*-
import asyncio
import logging

from loguru import logger  # https://github.com/Delgan/loguru

from handlers.admin.admin_handlers import register_admin_handlers
from handlers.payments.cryptomus_payments.cryptomus_commentator import register_cryptomus_program_com
from handlers.payments.cryptomus_payments.cryptomus_commentator_password import register_cryptomus_password_commentator
from handlers.payments.cryptomus_payments.cryptomus_password import register_cryptomus_password
from handlers.payments.cryptomus_payments.cryptomus_program import register_cryptomus_program
from handlers.payments.cryptomus_payments.cryptomus_training import register_cryptomus_training
from handlers.payments.payments import register_program_payments
from handlers.payments.yookassa_payments.yookassa_commentator import register_yookassa_program_com
from handlers.payments.yookassa_payments.yookassa_commentator_password import \
    register_yookassa_password_commentator_password
from handlers.payments.yookassa_payments.yookassa_password import register_yookassa_password
from handlers.payments.yookassa_payments.yookassa_program import register_yookassa_program
from handlers.payments.yookassa_payments.yookassa_training import register_yookassa_training
from handlers.user.ai_handlers import register_ai_handlers
from handlers.user.fag_handlers import fag_register_message_handler
from handlers.user.reference_handlers import register_faq_handler
from handlers.user.sending_log_file import sending_log_file_register_handler
from handlers.user.user_handlers import greeting_handler
from system.dispatcher import dp, bot

logger.add("logs/log.log", rotation="1 MB", compression="zip", level="INFO")  # Логирование программы
logger.add("logs/log_ERROR.log", rotation="1 MB", compression="zip", level="ERROR")  # Логирование программы


async def main() -> None:
    """Запуск бота https://t.me/h24service_bot"""

    await dp.start_polling(bot)

    #  ИИ
    register_ai_handlers()

    # Администрирование
    register_admin_handlers()  # Удаление системных сообщений

    # Рабата с пользователем бота
    greeting_handler()  # Пост приветствие пользователей бота
    fag_register_message_handler()  # Помощь по боту
    sending_log_file_register_handler()  # Отправка логов боту
    register_faq_handler()  # Регистрация FAQ

    # Меню оплата
    register_program_payments()  # Купить TelegramMaster 2.0, Помощь в настройке ПО, Пароль от TelegramMaster 2.0

    # Оплата yookassa
    register_yookassa_password()  # Покупка пароля TelegramMaster 2.0
    register_yookassa_password_commentator_password()  # Покупка пароля TelegramMaster_Commentator

    register_yookassa_program_com()  # Купить TelegramMaster_Commentator
    register_yookassa_program()  # Купить TelegramMaster 2.0
    register_yookassa_training()  # Оплата настройки ПО

    # Оплата Криптой
    register_cryptomus_password()  # Покупка пароля TelegramMaster 2.0
    register_cryptomus_password_commentator()  # Покупка пароля TelegramMaster_Commentator

    register_cryptomus_program()  # Покупка TelegramMaster 2.0
    register_cryptomus_program_com()  # Купить TelegramMaster_Commentator
    register_cryptomus_training()  # Покупка 'Помощь в настройке ПО (консультация)'


if __name__ == '__main__':
    try:
        logging.basicConfig()
        asyncio.run(main())
    except Exception as e:
        logger.exception(e)
