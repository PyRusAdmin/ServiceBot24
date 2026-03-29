# -*- coding: utf-8 -*-
import datetime

from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from loguru import logger

from db.settings_db import get_all_users
from system.dispatcher import bot, ADMIN_CHAT_ID

router = Router(name=__name__)


class AdminState(StatesGroup):
    """Состояния для админских команд"""
    waiting_for_broadcast_message = State()


@router.message(Command('admin_help'))
async def admin_help_handler(message: types.Message):
    """
    Справка по админским командам
    """
    # Проверяем, является ли пользователь администратором
    if str(message.from_user.id) != str(ADMIN_CHAT_ID):
        await message.answer("❌ У вас нет доступа к админским командам.")
        return

    help_text = """
🔧 <b>Админские команды бота</b> 🔧

📋 <b>Доступные команды:</b>

1️⃣ <b>/admin_help</b> - Показать эту справку

2️⃣ <b>/broadcast</b> - Начать рассылку сообщения всем пользователям

📝 <b>Как использовать рассылку:</b>

Шаг 1. Отправьте команду /broadcast

Шаг 2. Бот попросит вас ввести текст сообщения для рассылки

Шаг 3. Введите текст сообщения (можно использовать HTML-разметку)

Шаг 4. Бот покажет статистику: сколько всего пользователей и сколько сообщений отправлено

⚠️ <b>Важно:</b>
• Рассылка отправляется всем пользователям, которые хотя бы раз запускали бота
• Используйте разметку осторожно (HTML)
• Большие рассылки могут занять некоторое время

📊 <b>Пример использования:</b>
<code>/broadcast</code> → <code>Уважаемые пользователи! У нас обновился функционал...</code>
"""

    await message.answer(help_text, parse_mode="HTML")


@router.message(Command('broadcast'))
async def start_broadcast_handler(message: types.Message, state: FSMContext):
    """
    Начало рассылки сообщений пользователям
    """
    # Проверяем, является ли пользователь администратором
    if str(message.from_user.id) != str(ADMIN_CHAT_ID):
        await message.answer("❌ У вас нет доступа к этой команде.")
        return

    await message.answer(
        "📨 <b>Рассылка сообщений</b>\n\n"
        "Введите текст сообщения, которое вы хотите отправить всем пользователям:\n\n"
        "⚠️ Можно использовать HTML-разметку",
        parse_mode="HTML"
    )
    await state.set_state(AdminState.waiting_for_broadcast_message)


@router.message(AdminState.waiting_for_broadcast_message)
async def process_broadcast_message(message: types.Message, state: FSMContext):
    """
    Обработка сообщения для рассылки и отправка пользователям
    """
    # Проверяем, является ли пользователь администратором
    if str(message.from_user.id) != str(ADMIN_CHAT_ID):
        await message.answer("❌ У вас нет доступа к этой команде.")
        await state.clear()
        return

    broadcast_text = message.text
    logger.info(f"Администратор {message.from_user.id} начал рассылку")

    # Получаем всех пользователей из базы данных
    users = get_all_users()

    if not users:
        await message.answer("❌ В базе данных нет пользователей для рассылки.")
        await state.clear()
        return

    total_users = len(users)
    success_count = 0
    error_count = 0

    # Отправляем сообщение всем пользователям
    for user in users:
        try:
            await bot.send_message(
                chat_id=user['user_id'],
                text=broadcast_text,
                parse_mode="HTML"
            )
            success_count += 1
        except Exception as e:
            logger.error(f"Не удалось отправить сообщение пользователю {user['user_id']}: {e}")
            error_count += 1

    # Отправляем отчет администратору
    report = (
        f"✅ <b>Рассылка завершена</b>\n\n"
        f"📊 <b>Статистика:</b>\n"
        f"• Всего пользователей: {total_users}\n"
        f"• Успешно отправлено: {success_count}\n"
        f"• Ошибок: {error_count}\n\n"
        f"🕒 Время завершения: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

    await message.answer(report, parse_mode="HTML")
    logger.info(f"Рассылка завершена. Успешно: {success_count}, Ошибок: {error_count}")
    await state.clear()


@router.message(Command('stats'))
async def stats_handler(message: types.Message):
    """
    Показывает статистику пользователей бота
    """
    # Проверяем, является ли пользователь администратором
    if str(message.from_user.id) != str(ADMIN_CHAT_ID):
        await message.answer("❌ У вас нет доступа к этой команде.")
        return

    users = get_all_users()
    total_users = len(users) if users else 0

    stats_text = (
        f"📊 <b>Статистика бота</b> 📊\n\n"
        f"👥 Всего пользователей: {total_users}\n\n"
        f"🕒 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

    await message.answer(stats_text, parse_mode="HTML")
