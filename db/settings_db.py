import sqlite3

from loguru import logger

from .database import connect_db


def add_user_if_not_exists(user_id):
    """
    Добавляет пользователя в базу данных, если он там еще не зарегистрирован.
    :param user_id: ID пользователя
    """
    with sqlite3.connect('setting/user_data.db') as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (id) VALUES (?)', (user_id,))
        conn.commit()


def save_payment_info(user_id, first_name, last_name, username, invoice_json, product, date, status):
    """
    Функция для сохранения информации о платеже
    :param user_id: ID пользователя
    :param first_name: Имя пользователя
    :param last_name: Фамилия пользователя
    :param username: Имя пользователя в Telegram
    :param invoice_json: Информация о платеже
    :param product: Название продукта
    :param date: Дата платежа
    :param status: Статус платежа
    """
    with sqlite3.connect('setting/user_data.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users_pay (user_id, first_name, last_name, username, payment_info,
                                                                product, date, payment_status)''')
        cursor.execute('''INSERT INTO users_pay (user_id, first_name, last_name, username, payment_info, 
                            product, date, payment_status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                       (user_id, first_name, last_name, username, invoice_json, product, date, status))
        conn.commit()


def read_amount_db():
    """Функция для получения суммы из базы данных"""
    try:
        conn = connect_db()  # Инициализация базы данных SQLite
        cursor = conn.cursor()
        cursor.execute('''SELECT amount FROM settings''')
        result = cursor.fetchone()
        conn.close()
        return result[0]
    except Exception as e:
        logger.exception(f"Ошибка при чтении базы данных: {e}")


def clear_amount():
    """Функция для очистки суммы в базе данных"""
    try:
        conn = connect_db()  # Инициализация базы данных SQLite
        cursor = conn.cursor()
        cursor.execute('''DELETE FROM settings''')
        conn.commit()
        conn.close()
    except Exception as e:
        logger.exception(f"Ошибка при очистке базы данных: {e}")


def checking_for_presence_in_the_user_database(user_id):
    # Инициализация базы данных SQLite
    conn = connect_db()  # Инициализация базы данных SQLite
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY)')
    # Проверка наличия ID в базе данных
    cursor.execute('SELECT id FROM users WHERE id = ?', (user_id,))
    result = cursor.fetchone()
    return result


def writing_to_the_database_about_a_new_user(chat_id, chat_title, user_id, username, first_name, last_name, date_now):
    """Запись данных о новом пользователе"""
    # Записываем данные в базу данных
    conn = connect_db()  # Инициализация базы данных SQLite
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


if __name__ == '__main__':
    read_amount_db()
    clear_amount()
