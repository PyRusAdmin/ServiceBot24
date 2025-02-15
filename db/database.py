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


if __name__ == "__main__":
    connect_db()
