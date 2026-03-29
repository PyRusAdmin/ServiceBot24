# -*- coding: utf-8 -*-
import datetime  # Дата

from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from loguru import logger

from db.settings_db import save_user_activity
from keyboards.user_keyboards import greeting_keyboards, payment_keyboards
from messages.messages import greeting_post, payment_goods_and_services_post
from system.dispatcher import bot

router = Router(name=__name__)


@router.message(Command('start'))
async def greeting(message: types.Message, state: FSMContext):
    """
    Обработчик команды /start, он же пост приветствия
    :param message: объект класса Message
    :param state: Функция clear очищает все сохраненные ранее значения
    """
    logger.info(f"Получена команда /start от {message.from_user.id}")
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


@router.callback_query(F.data == 'start_menu_keyboard')
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


@router.callback_query(F.data == 'payment_goods_and_services')
async def payment_goods_and_services_handler(callback_query: types.CallbackQuery, state: FSMContext):
    """Обработчик кнопки оплаты товаров"""
    await state.clear()
    await bot.send_message(
        callback_query.message.chat.id,
        payment_goods_and_services_post,
        reply_markup=payment_keyboards(),
        parse_mode="HTML",
    )



