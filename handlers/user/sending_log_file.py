# -*- coding: utf-8 -*-
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery

from system.dispatcher import dp, form_router, bot, ADMIN_CHAT_ID  # Подключение к боту и диспетчеру пользователя


class Form(StatesGroup):
    file = State()


@form_router.callback_query(F.data == "sending_file")
async def sending_log_file(callback_query: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(Form.file)
    chat_id = callback_query.message.chat.id
    await bot.send_message(chat_id, "Пожалуйста, отправьте файл, который вы хотите отправить администратору.")


@form_router.message(Form.file)
async def sending_log_file_handler(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.document)

    file_id = None
    if message.document:
        file_id = message.document.file_id
    elif message.photo:
        file_id = message.photo[-1].file_id
    elif message.video:
        file_id = message.video.file_id
    if file_id:
        # Отправка файла администратору по его file_id
        admin_chat_id = ADMIN_CHAT_ID  # Замените на ID чата администратора
        await bot.send_document(admin_chat_id, document=file_id, caption=f"Пользователь:\n"
                                                                         f"ID {message.from_user.id},\n"
                                                                         f"Username: @{message.from_user.username},\n"
                                                                         f"Имя: {message.from_user.first_name},\n"
                                                                         f"Фамилия: {message.from_user.last_name},\n\n"
                                                                         f"Отправил файл")
        # Очищаем состояние
        await state.clear()
        await message.reply("Ваш файл успешно отправлен администратору.")


def sending_log_file_register_handler():
    dp.message.register(sending_log_file)
