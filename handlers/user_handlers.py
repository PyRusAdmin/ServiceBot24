from aiogram import types  # Типы пользователя
from aiogram.dispatcher import FSMContext  # Состояния пользователя
from keyboards.user_keyboards import greeting_keyboards  # Клавиатуры поста приветствия
from messages.user_messages import greeting_post  # Пояснение для пользователя FAG

from system.dispatcher import dp  # Подключение к боту и диспетчеру пользователя


@dp.message_handler(commands=['start'])
async def greeting(message: types.Message, state: FSMContext):
    """Обработчик команды /start, он же пост приветствия"""
    await state.finish()
    await state.reset_state()
    keyboards_greeting = greeting_keyboards()
    # Клавиатура для Калькулятора цен или Контактов
    await message.reply(greeting_post, reply_markup=keyboards_greeting, disable_web_page_preview=True,
                        parse_mode=types.ParseMode.HTML)


def greeting_handler():
    """Регистрируем handlers для калькулятора"""
    dp.register_message_handler(greeting)  # Обработчик команды /start, он же пост приветствия
