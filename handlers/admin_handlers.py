import datetime
import sqlite3
from aiogram import types, F
from loguru import logger
from system.dispatcher import dp, bot


def writing_to_the_database_about_a_new_user(chat_id, chat_title, user_id, username, first_name, last_name, date_now):
    """Запись данных о новом пользователе"""
    # Записываем данные в базу данных
    conn = sqlite3.connect('setting/user_data.db')
    cursor = conn.cursor()
    cursor.execute(
        f"CREATE TABLE IF NOT EXISTS group_members (chat_id, chat_title, user_id, username, first_name, last_name, "
        "date_joined)"
    )
    cursor.execute(
        f"INSERT INTO group_members (chat_id, chat_title, user_id, username, first_name, last_name, date_joined) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (chat_id, chat_title, user_id, username, first_name, last_name, date_now)
    )
    conn.commit()
    conn.close()


@dp.message(F.new_chat_members)
async def deleting_message_about_adding_new_group_member(message: types.Message):
    """
    Удаляем сообщение о новом участнике группы и записываем данные в базу данных
    chat_id - ID чата
    chat_title = Название чата
    user_id = ID пользователя, который зашел в группу
    username = Username пользователя, который вступил в группу
    first_name = Имя пользователя который вступил в группу
    last_name = Фамилия пользователя который вступил в группу
    """
    chat_id = message.chat.id  # Получаем ID чата
    logger.info(chat_id)
    chat_title = message.chat.title  # Получаем название чата
    user_id = message.new_chat_members[0].id  # Получаем ID пользователя, который зашел в группу
    username = message.new_chat_members[0].username  # Получаем username пользователя, который вступил в группу
    first_name = message.new_chat_members[0].first_name  # Получаем имя пользователя который вступил в группу
    last_name = message.new_chat_members[0].last_name  # Получаем фамилию пользователя который вступил в группу
    date_now = datetime.datetime.now()  # Дата вступления участника в группу
    writing_to_the_database_about_a_new_user(chat_id, chat_title, user_id, username, first_name, last_name,
                                             date_now)
    logger.info(f"Новый участник группы: {username}, {first_name}, {last_name}, {date_now}, {chat_title}, {chat_id}")
    await bot.delete_message(chat_id, message.message_id)  # Удаляем сообщение о новом участнике группы


@dp.message(F.left_chat_member)
async def deleting_a_message_about_a_member_has_left_the_group(message: types.Message):
    """
    Удаляем сообщение о покинувшем участнике группы и записываем данные в базу данных
    chat_id - ID чата
    chat_title = Название чата
    user_id = ID пользователя, который зашел в группу
    username = Username пользователя, который вступил в группу
    first_name = Имя пользователя который вступил в группу
    last_name = Фамилия пользователя который вступил в группу
    """
    chat_id = message.chat.id  # Получаем ID чата с которого пользователь вышел
    chat_title = message.chat.title  # Получаем название с которого пользователь вышел
    user_id = message.left_chat_member.id  # Получаем ID пользователя, который вышел с чата
    username = message.left_chat_member.username  # Получаем username пользователя с которого пользователь вышел
    first_name = message.left_chat_member.first_name  # Получаем имя пользователя, того что вышел с группы
    last_name = message.left_chat_member.last_name  # Получаем фамилию пользователя, того что вышел с группы
    date_left = datetime.datetime.now()  # Дата выхода пользователя с группы
    logger.info(f"Участник покинул группу: {username}, {first_name}, {last_name}, {date_left}, {chat_title}, {chat_id}, {user_id}")
    await bot.delete_message(message.chat.id, message.message_id)  # Удаляем сообщение о покинувшем участнике группы
