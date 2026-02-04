# -*- coding: utf-8 -*-
import datetime  # Дата

from aiogram import F
from aiogram import types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from loguru import logger

from db.settings_db import save_user_activity, add_user_to_db, is_user_in_db
from keyboards.user_keyboards import greeting_keyboards, payment_keyboards  # Клавиатуры поста приветствия
from messages.messages import greeting_post, payment_goods_and_services_post  # Пояснение для пользователя FAG
from states.states import SomeState
from system.dispatcher import dp, bot  # Подключение к боту и диспетчеру пользователя


@dp.message(Command("pass"))
async def send_pass(message: types.Message, state: FSMContext):
    """Обработчик команды /pass, для отправки пароля в бота"""
    await message.answer(f'Введите пароль: {message.text}')
    await state.set_state(SomeState.some_state)  # Обновляем состояние


@dp.message(SomeState.some_state)
async def greeting(message: types.Message, state: FSMContext):
    """Обработчик состояния some_state, он же пост приветствия"""
    text = message.text  # Получаем текст сообщения
    # Используем with open для открытия файла с использованием кодека utf-8
    with open("setting/password/TelegramMaster-PRO/password.txt", "w", encoding='utf-8') as file:
        file.write(text)
    await state.clear()


@dp.message(Command('start'))
async def greeting(message: types.Message, state: FSMContext):
    """
    Обработчик команды /start, он же пост приветствия
    :param message: объект класса Message
    :param state: Функция clear очищает все сохраненные ранее значения
    """
    await state.clear()  # Стираем предыдущее сообщение
    # Записываем данные пользователя в базу данных
    save_user_activity(
        user_id=message.from_user.id,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        username=message.from_user.username,
        date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    logger.info(
        f'Запустили бота: {message.from_user.id, message.from_user.username, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    # Клавиатура для Калькулятора цен или Контактов
    await message.answer(
        text=greeting_post,
        reply_markup=greeting_keyboards(),
        disable_web_page_preview=True,
        parse_mode="HTML"
    )


@dp.callback_query(F.data == 'start_menu_keyboard')
async def start_menu_no_edit(callback_query: types.CallbackQuery, state: FSMContext):
    """Обработчик команды /start, он же пост приветствия"""
    await state.clear()
    # Записываем данные пользователя в базу данных
    save_user_activity(
        callback_query.from_user.id,
        callback_query.from_user.first_name,
        callback_query.from_user.last_name,
        callback_query.from_user.username,
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    logger.info(
        f'Запустили бота: {callback_query.from_user.id, callback_query.from_user.username, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    await bot.send_message(
        callback_query.message.chat.id,
        greeting_post,
        reply_markup=greeting_keyboards(),
        parse_mode="HTML",
    )


@dp.callback_query(F.data == 'payment_goods_and_services')
async def payment_goods_and_services_handler(callback_query: types.CallbackQuery, state: FSMContext):
    """Обработчик кнопки оплаты товаров"""
    await state.clear()
    await bot.send_message(
        callback_query.message.chat.id,
        payment_goods_and_services_post,
        reply_markup=payment_keyboards(),
        parse_mode="HTML",
    )


@dp.message(Command('id'))
async def process_id_command(message: types.Message):
    """Обработчик команды /id"""
    try:
        user_id = int(message.text.split()[1])
        result = is_user_in_db(user_id)  # Запись ID в базу данных
        if result is None:
            add_user_to_db(user_id)
            await message.reply(f"ID {user_id} успешно записан в базу данных.")
        else:
            await message.reply(f"ID {user_id} уже существует в базе данных.")
    except (IndexError, ValueError):
        await message.reply("Используйте команду /id followed by ваш ID.")
    except Exception as error:
        logger.exception(error)


def greeting_handler():
    dp.message.register(greeting)
    dp.message.register(process_id_command)
    dp.message.register(payment_goods_and_services_handler)
