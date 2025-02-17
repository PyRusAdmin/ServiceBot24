# -*- coding: utf-8 -*-
import sqlite3

from loguru import logger


def connect_db():
    """Подключение к базе данных"""
    try:
        conn = sqlite3.connect("setting/user_data.db")
        return conn
    except Exception as e:
        logger.exception(f"Ошибка подключения к базе данных: {e}")
        raise


def save_payment_info(user_id, first_name, last_name, username, invoice_json, product, date, status):
    """Сохраняет информацию о платеже"""
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users_pay (
                            user_id INTEGER,
                            first_name TEXT,
                            last_name TEXT,
                            username TEXT,
                            payment_info TEXT,
                            product TEXT,
                            date TEXT,
                            payment_status TEXT)''')
        cursor.execute('''INSERT INTO users_pay (user_id, first_name, last_name, username, payment_info, 
                        product, date, payment_status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                       (user_id, first_name, last_name, username, invoice_json, product, date, status))
        conn.commit()


def check_user_payment(user_id, product_name):
    """Проверяет, покупал ли пользователь продукт"""
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''SELECT 1 FROM users_pay WHERE user_id = ? AND product = ?''', (user_id, product_name))
        return cursor.fetchone() is not None


def add_user_to_db(user_id):
    """Добавляет пользователя в базу данных"""
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY)''')
        cursor.execute('''INSERT OR IGNORE INTO users (id) VALUES (?)''', (user_id,))
        conn.commit()


def save_user_activity(user_id, first_name, last_name, username, date):
    """Сохраняет активность пользователя"""
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users_run (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER, 
                            first_name TEXT, 
                            last_name TEXT, 
                            username TEXT, 
                            date TEXT)''')
        cursor.execute(
            '''INSERT INTO users_run (user_id, first_name, last_name, username, date) VALUES (?, ?, ?, ?, ?)''',
            (user_id, first_name, last_name, username, date))
        conn.commit()


def save_user_wish(user_id, clean_response):
    """Сохраняет пожелание пользователя"""
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS user_wishes (user_id INTEGER, wish TEXT)''')
        cursor.execute('''INSERT INTO user_wishes (user_id, wish) VALUES (?, ?)''', (user_id, clean_response))
        conn.commit()


def add_user_if_not_exists(user_id):
    """Добавляет пользователя, если он еще не зарегистрирован"""
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''INSERT OR IGNORE INTO users (id) VALUES (?)''', (user_id,))
        conn.commit()


def is_user_in_db(user_id):
    """Проверяет, зарегистрирован ли пользователь"""
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''SELECT 1 FROM users WHERE id = ?''', (user_id,))
        return cursor.fetchone() is not None


def add_new_group_member(chat_id, chat_title, user_id, username, first_name, last_name, date_now):
    """
    Добавляет нового участника в базу данных
    :param chat_id: id чата
    :param chat_title: название чата
    :param user_id: id пользователя
    :param username: username пользователя
    :param first_name: имя пользователя
    :param last_name: фамилия пользователя
    :param date_now: дата и время
    """
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS group_members (
                            chat_id INTEGER,
                            chat_title TEXT,
                            user_id INTEGER,
                            username TEXT,
                            first_name TEXT,
                            last_name TEXT,
                            date_joined TEXT)''')
        cursor.execute('''INSERT INTO group_members (chat_id, chat_title, user_id, username, first_name, last_name, date_joined)
                          VALUES (?, ?, ?, ?, ?, ?, ?)''',
                       (chat_id, chat_title, user_id, username, first_name, last_name, date_now))
        conn.commit()
