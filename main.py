from aiogram import executor

from system.dispatcher import dp


def main():
    executor.start_polling(dp, skip_updates=True)


if __name__ == '__main__':
    try:
        main()  # Запуск бота
    except Exception as e:
        print(e)
