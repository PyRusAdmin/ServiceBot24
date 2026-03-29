# -*- coding: utf-8 -*-
"""
Модуль определяет группы состояний для конечного автомата (FSM) в Telegram-боте.

Содержит классы групп состояний, используемых для управления состоянием диалога с пользователем.
"""
from aiogram.fsm.state import StatesGroup, State


class Form(StatesGroup):
    """
    Группа состояний для формы загрузки файла.

    Состояния:
        file (State): Состояние ожидания загрузки файла от пользователя.
    """
    file = State()


class WishState(StatesGroup):
    """
    Состояния для обработки пожеланий пользователей.
    """
    waiting_for_wish = State()


class AdminState(StatesGroup):
    """
    Состояния для админских команд.
    """
    waiting_for_broadcast_message = State()
    waiting_for_password = State()
