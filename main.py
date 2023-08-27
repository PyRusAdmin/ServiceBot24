from aiogram import executor

from handlers.user_handlers import greeting_handler
from system.dispatcher import dp


def main() -> None:
    """Запуск бота https://t.me/h24service_bot"""
    executor.start_polling(dp, skip_updates=True)
    greeting_handler()


if __name__ == '__main__':
    try:
        main()  # Запуск бота
    except Exception as e:
        print(e)
