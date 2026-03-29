# -*- coding: utf-8 -*-
import datetime
import sqlite3

from loguru import logger
from peewee import *

# Подключаемся к той же базе
db = SqliteDatabase("setting/user_data.db")


class BaseModel(Model):
    class Meta:
        database = db


def connect_db():
    """Подключение к базе данных"""
    try:
        conn = sqlite3.connect("setting/user_data.db")
        return conn
    except Exception as e:
        logger.exception(f"Ошибка подключения к базе данных: {e}")
        raise


class UserPayment(BaseModel):
    id = AutoField()
    user_id = IntegerField()
    first_name = TextField(null=True)
    last_name = TextField(null=True)
    username = TextField(null=True)
    payment_info = TextField()  # ← указываем реальное имя колонки
    product = TextField()
    date = TextField()
    payment_status = TextField()  # ← и здесь тоже

    # price = TextField(null=True)

    class Meta:
        table_name = 'users_pay'
        # если хочешь индекс по пользователю + продукту (ускоряет поиск "купил ли он это")
        indexes = (
            (('user_id', 'product'), False),
        )


def save_payment_info_user(table_name, user_id, first_name, last_name, username, invoice_json, product, date, status,
                           price):
    """
    Сохраняет информацию о платеже

    :param table_name: имя таблицы
    :param user_id: id пользователя
    :param first_name: имя пользователя
    :param last_name: фамилия пользователя
    :param username: ник пользователя
    :param invoice_json: json с информацией о платеже
    :param product: название продукта
    :param date: дата платежа
    :param status: статус платежа
    :param price: цена продукта
    """
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute(f'''CREATE TABLE IF NOT EXISTS {table_name} (user_id INTEGER, first_name TEXT, last_name TEXT,
                                                                username TEXT, payment_info TEXT, product TEXT,
                                                                date TEXT, payment_status TEXT, price TEXT)''')
        cursor.execute(f'''INSERT INTO {table_name} (user_id, first_name, last_name, username, payment_info, 
                        product, date, payment_status, price) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                       (user_id, first_name, last_name, username, invoice_json, product, date, status, price))
        conn.commit()


def save_payment_info(user_id, first_name, last_name, username, invoice_json, product, date, status):
    """Сохраняет информацию о платеже"""
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users_pay (user_id INTEGER, first_name TEXT, last_name TEXT,
                                                                username TEXT, payment_info TEXT, product TEXT,
                                                                date TEXT, payment_status TEXT)''')
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
    """
    Сохраняет активность пользователя.
    Если пользователь уже существует - обновляет его данные (username, first_name, last_name, date).
    Неизменным остается только user_id (уникальный ID Telegram).
    """
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users_run (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER UNIQUE,
                                                                first_name TEXT, last_name TEXT, username TEXT,
                                                                date TEXT)''')
        # Проверяем, существует ли пользователь
        cursor.execute('''SELECT id FROM users_run WHERE user_id = ?''', (user_id,))
        existing = cursor.fetchone()
        
        if existing:
            # Обновляем существующую запись
            cursor.execute('''UPDATE users_run 
                              SET first_name = ?, last_name = ?, username = ?, date = ? 
                              WHERE user_id = ?''',
                           (first_name, last_name, username, date, user_id))
        else:
            # Создаем новую запись
            cursor.execute('''INSERT INTO users_run (user_id, first_name, last_name, username, date) 
                              VALUES (?, ?, ?, ?, ?)''',
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
        cursor.execute('''CREATE TABLE IF NOT EXISTS group_members (chat_id INTEGER, chat_title TEXT, user_id INTEGER,
                                                                    username TEXT, first_name TEXT, last_name TEXT,
                                                                    date_joined TEXT)''')
        cursor.execute('''INSERT INTO group_members (chat_id, chat_title, user_id, username, first_name, last_name, date_joined)
                          VALUES (?, ?, ?, ?, ?, ?, ?)''',
                       (chat_id, chat_title, user_id, username, first_name, last_name, date_now))
        conn.commit()


def get_all_users():
    """
    Получает всех пользователей из таблицы users_run
    :return: список словарей с данными пользователей [{'user_id': 123, 'first_name': '...', ...}, ...]
    """
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''SELECT user_id, first_name, last_name, username, date FROM users_run''')
        rows = cursor.fetchall()

        users = []
        for row in rows:
            users.append({
                'user_id': row[0],
                'first_name': row[1],
                'last_name': row[2],
                'username': row[3],
                'date': row[4]
            })
        return users


# ============================================================================
# Модели Peewee для работы с паролями продуктов
# ============================================================================

class ProductPassword(BaseModel):
    """
    Модель для хранения паролей продуктов
    """
    product_name = TextField(unique=True, primary_key=True)  # Название продукта (первичный ключ)
    password = TextField()  # Пароль
    updated_at = DateTimeField(default=datetime.datetime.now)  # Дата последнего обновления

    class Meta:
        table_name = 'product_passwords'
        indexes = (
            (('product_name',), True),  # Уникальный индекс по product_name
        )


def init_password_tables():
    """
    Инициализация таблиц для хранения паролей
    """
    db.connect()
    db.create_tables([ProductPassword], safe=True)
    db.close()


def get_product_password(product_name: str) -> str | None:
    """
    Получает пароль для продукта из базы данных
    :param product_name: название продукта
    :return: пароль или None, если не найден
    """
    try:
        password_record = ProductPassword.get(ProductPassword.product_name == product_name)
        return password_record.password
    except ProductPassword.DoesNotExist:
        return None


def set_product_password(product_name: str, password: str) -> bool:
    """
    Устанавливает или обновляет пароль для продукта
    :param product_name: название продукта
    :param password: пароль
    :return: True если успешно, False если ошибка
    """
    try:
        # Проверяем, существует ли запись
        try:
            password_record = ProductPassword.get(ProductPassword.product_name == product_name)
            # Обновляем существующую запись
            password_record.password = password
            password_record.updated_at = datetime.datetime.now()
            password_record.save()
        except ProductPassword.DoesNotExist:
            # Создаем новую запись
            ProductPassword.create(
                product_name=product_name,
                password=password,
                updated_at=datetime.datetime.now()
            )
        return True
    except Exception as e:
        logger.exception(f"Ошибка при установке пароля для {product_name}: {e}")
        return False


def get_all_product_passwords() -> list:
    """
    Получает все пароли продуктов
    :return: список словарей [{'product_name': '...', 'password': '...', 'updated_at': ...}, ...]
    """
    try:
        passwords = ProductPassword.select()
        return [
            {
                'product_name': p.product_name,
                'password': p.password,
                'updated_at': p.updated_at.strftime("%Y-%m-%d %H:%M:%S")
            }
            for p in passwords
        ]
    except Exception as e:
        logger.exception(f"Ошибка при получении всех паролей: {e}")
        return []
