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


def save_payment_info(data_payment):
    """Сохраняет информацию о платеже"""
    table_name = data_payment.get('table_name', 'users_pay')
    
    if table_name == 'users_pay_search':
        # Для TelegramMaster-Search-GPT используем отдельную таблицу
        save_payment_info_user(
            table_name=table_name,
            user_id=data_payment.get('user_id'),
            first_name=data_payment.get('first_name'),
            last_name=data_payment.get('last_name'),
            username=data_payment.get('username'),
            invoice_json=data_payment.get('payment_info'),
            product=data_payment.get('product'),
            date=data_payment.get('date'),
            status=data_payment.get('payment_status'),
            price=data_payment.get('price')
        )
    else:
        # Для остальных продуктов используем стандартную таблицу users_pay
        UserPayment.create(
            user_id=data_payment.get('user_id'),
            first_name=data_payment.get('first_name'),
            last_name=data_payment.get('last_name'),
            username=data_payment.get('username'),
            payment_info=data_payment.get('payment_info'),
            product=data_payment.get('product'),
            date=data_payment.get('date'),
            payment_status=data_payment.get('payment_status')
        )


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


# ============================================================================
# Модели для MaxMaster и аренды сервера
# ============================================================================

class MaxMasterPassword(BaseModel):
    """
    Модель для хранения пароля MaxMaster
    """
    id = AutoField(primary_key=True)
    password = TextField()  # Пароль от архива MaxMaster
    updated_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        table_name = 'maxmaster_password'


class ServerRent(BaseModel):
    """
    Модель для хранения информации об аренде сервера
    """
    id = AutoField(primary_key=True)
    user_id = IntegerField()  # ID пользователя в Telegram
    username = TextField(null=True)  # Username пользователя
    first_name = TextField(null=True)  # Имя пользователя
    last_name = TextField(null=True)  # Фамилия пользователя
    months = IntegerField()  # Количество месяцев аренды (1-12)
    start_date = DateTimeField()  # Дата начала аренды
    end_date = DateTimeField()  # Дата окончания аренды
    payment_amount = DecimalField(max_digits=10, decimal_places=2)  # Сумма оплаты
    payment_method = TextField()  # Способ оплаты: 'yookassa', 'stars', 'cryptomus'
    payment_date = DateTimeField(default=datetime.datetime.now)  # Дата оплаты
    is_active = BooleanField(default=True)  # Активна ли аренда

    class Meta:
        table_name = 'server_rent'
        indexes = (
            (('user_id', 'is_active'), False),  # Индекс для поиска активных аренд пользователя
        )


class MaxMasterSale(BaseModel):
    """
    Модель для хранения информации о продаже MaxMaster
    """
    id = AutoField(primary_key=True)
    user_id = IntegerField()  # ID пользователя в Telegram
    username = TextField(null=True)
    first_name = TextField(null=True)
    last_name = TextField(null=True)
    purchase_date = DateTimeField(default=datetime.datetime.now)  # Дата покупки
    payment_amount = DecimalField(max_digits=10, decimal_places=2)  # Сумма оплаты
    payment_method = TextField()  # Способ оплаты: 'yookassa', 'stars', 'cryptomus'

    class Meta:
        table_name = 'maxmaster_sales'


def init_new_products_tables():
    """
    Инициализация таблиц для MaxMaster и аренды сервера
    """
    db.connect()
    db.create_tables([MaxMasterPassword, ServerRent, MaxMasterSale], safe=True)
    db.close()


# Функции для MaxMaster Password
def set_maxmaster_password(password: str) -> bool:
    """Устанавливает пароль для MaxMaster"""
    try:
        # Проверяем, существует ли запись
        record = MaxMasterPassword.get_or_none()
        if record:
            record.password = password
            record.updated_at = datetime.datetime.now()
            record.save()
        else:
            MaxMasterPassword.create(password=password, updated_at=datetime.datetime.now())
        return True
    except Exception as e:
        logger.exception(f"Ошибка при установке пароля MaxMaster: {e}")
        return False


def get_maxmaster_password() -> str | None:
    """Получает пароль для MaxMaster"""
    try:
        record = MaxMasterPassword.get_or_none()
        return record.password if record else None
    except Exception as e:
        logger.exception(f"Ошибка при получении пароля MaxMaster: {e}")
        return None


# Функции для ServerRent
def add_server_rent(
        user_id: int,
        username: str,
        first_name: str,
        last_name: str,
        months: int,
        payment_amount: float,
        payment_method: str,
        start_date: datetime.datetime,
        end_date: datetime.datetime
) -> int:
    """
    Добавляет запись об аренде сервера
    :return: ID записи
    """
    try:
        rent = ServerRent.create(
            user_id=user_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            months=months,
            payment_amount=payment_amount,
            payment_method=payment_method,
            start_date=start_date,
            end_date=end_date
        )
        return rent.id
    except Exception as e:
        logger.exception(f"Ошибка при добавлении аренды сервера: {e}")
        return -1


def get_active_server_rent(user_id: int) -> ServerRent | None:
    """Получает активную аренду сервера для пользователя"""
    try:
        return ServerRent.get_or_none(
            (ServerRent.user_id == user_id) & (ServerRent.is_active == True)
        )
    except Exception as e:
        logger.exception(f"Ошибка при получении аренды сервера: {e}")
        return None


def get_expiring_rents(days_until: int = 3) -> list:
    """
    Получает аренды, которые истекают через days_until дней
    :param days_until: за сколько дней до окончания предупреждать
    :return: список истекающих аренд
    """
    try:
        from peewee import fn
        cutoff_date = datetime.datetime.now() + datetime.timedelta(days=days_until)
        return list(ServerRent.select().where(
            (ServerRent.is_active == True) &
            (ServerRent.end_date <= cutoff_date) &
            (ServerRent.end_date >= datetime.datetime.now())
        ))
    except Exception as e:
        logger.exception(f"Ошибка при получении истекающих аренд: {e}")
        return []


def get_expired_rents() -> list:
    """Получает аренды, у которых истек срок"""
    try:
        return list(ServerRent.select().where(
            (ServerRent.is_active == True) &
            (ServerRent.end_date < datetime.datetime.now())
        ))
    except Exception as e:
        logger.exception(f"Ошибка при получении просроченных аренд: {e}")
        return []


def deactivate_server_rent(rent_id: int) -> bool:
    """Деактивирует аренду сервера"""
    try:
        rent = ServerRent.get_by_id(rent_id)
        rent.is_active = False
        rent.save()
        return True
    except Exception as e:
        logger.exception(f"Ошибка при деактивации аренды: {e}")
        return False


# Функции для MaxMasterSale
def add_maxmaster_sale(
        user_id: int,
        username: str,
        first_name: str,
        last_name: str,
        payment_amount: float,
        payment_method: str
) -> int:
    """
    Добавляет запись о продаже MaxMaster
    :return: ID записи
    """
    try:
        sale = MaxMasterSale.create(
            user_id=user_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            payment_amount=payment_amount,
            payment_method=payment_method
        )
        return sale.id
    except Exception as e:
        logger.exception(f"Ошибка при добавлении продажи MaxMaster: {e}")
        return -1
