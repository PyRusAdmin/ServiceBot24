# -*- coding: utf-8 -*-
import datetime

from aiogram import types, F

from db.settings_db import add_new_group_member
from system.dispatcher import dp, bot


@dp.message(F.new_chat_members)
async def deleting_message_about_adding_new_group_member(message: types.Message):
    """
    Удаляем сообщение о новом участнике группы и записываем данные в базу данных
    :param message: сообщение, которое было отправлено
    """
    # Добавляет нового участника в базу данных
    add_new_group_member(
        chat_id=message.chat.id,  # Получаем ID чата
        chat_title=message.chat.title,  # Получаем название чата
        user_id=message.new_chat_members[0].id,  # Получаем ID пользователя, который зашел в группу
        username=message.new_chat_members[0].username,  # Получаем username пользователя, который вступил в группу
        first_name=message.new_chat_members[0].first_name,  # Получаем имя пользователя который вступил в группу
        last_name=message.new_chat_members[0].last_name,  # Получаем фамилию пользователя который вступил в группу
        date_now=datetime.datetime.now(),  # Дата вступления участника в группу
    )
    await bot.delete_message(message.chat.id, message.message_id)  # Удаляем сообщение о новом участнике группы


@dp.message(F.left_chat_member)
async def deleting_a_message_about_a_member_has_left_the_group(message: types.Message):
    """
    Удаляем сообщение о покинувшем участнике группы и записываем данные в базу данных
    :param message: сообщение, которое было отправлено
    """
    await bot.delete_message(message.chat.id, message.message_id)  # Удаляем сообщение о покинувшем участнике группы


def register_admin_handlers():
    dp.register_message_handler(deleting_message_about_adding_new_group_member, F.new_chat_members)
    dp.register_message_handler(deleting_a_message_about_a_member_has_left_the_group, F.left_chat_member)
