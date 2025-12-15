# -*- coding: utf-8 -*-
from aiogram.fsm.state import StatesGroup, State


class Form(StatesGroup):
    file = State()


class SomeState(StatesGroup):
    some_state = State()  # Пример состояния, можно добавить дополнительные состояния
