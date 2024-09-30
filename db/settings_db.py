from .database import connect_db
from loguru import logger


def update_amount_db(amount):
    """Функция для обновления суммы в базе данных"""
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS settings (amount)''')
        cursor.execute('''INSERT INTO settings (amount) VALUES (?)''', (amount,))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.exception(f"Ошибка при обновлении базы данных: {e}")


def read_amount_db():
    """Функция для получения суммы из базы данных"""
    try:
        conn = connect_db()
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
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('''DELETE FROM settings''')
        conn.commit()
        conn.close()
    except Exception as e:
        logger.exception(f"Ошибка при очистке базы данных: {e}")



def checking_for_presence_in_the_user_database(user_id):
    # Инициализация базы данных SQLite
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY)')
    # Проверка наличия ID в базе данных
    cursor.execute('SELECT id FROM users WHERE id = ?', (user_id,))
    result = cursor.fetchone()
    return result

if __name__ == '__main__':
    read_amount_db()
    clear_amount()