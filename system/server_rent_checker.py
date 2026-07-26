# -*- coding: utf-8 -*-
"""
Задача проверки сроков оплаты сервера
Отправляет уведомления пользователям и админу об истекающей аренде
"""
import asyncio
import datetime

from loguru import logger

from db.settings_db import get_expiring_rents, get_expired_rents, deactivate_server_rent
from system.dispatcher import bot
import os
from dotenv import load_dotenv

load_dotenv()
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")


async def check_server_rent_expiration():
    """
    Проверяет истекающие и истекшие аренды сервера
    Отправляет уведомления пользователям и админу
    """
    try:
        logger.info("Запуск проверки сроков аренды сервера...")

        # Получаем аренды, которые истекают через 3 дня
        expiring_rents = get_expiring_rents(days_until=3)

        for rent in expiring_rents:
            days_left = (rent.end_date - datetime.datetime.now()).days

            # Отправляем уведомление пользователю
            try:
                await bot.send_message(
                    chat_id=rent.user_id,
                    text=f"⚠️ <b>Истекает срок аренды сервера!</b>\n\n"
                         f"📅 Ваша аренда сервера истекает через <b>{days_left} {'день' if days_left == 1 else 'дня' if days_left < 5 else 'дней'}</b>.\n\n"
                         f"📅 Дата окончания: {rent.end_date.strftime('%d.%m.%Y %H:%M')}\n"
                         f"💰 Оплачено месяцев: {rent.months}\n\n"
                         f"Для продления аренды обратитесь к @PyAdminRU или используйте команду /start для выбора нового срока.",
                    parse_mode="HTML"
                )
                logger.info(
                    f"Отправлено уведомление пользователю {rent.user_id} об истечении аренды через {days_left} дн.")
            except Exception as e:
                logger.error(f"Не удалось отправить уведомление пользователю {rent.user_id}: {e}")

            # Отправляем уведомление админу
            try:
                await bot.send_message(
                    chat_id=ADMIN_CHAT_ID,
                    text=f"⚠️ <b>Истекает аренда сервера!</b>\n\n"
                         f"👤 Пользователь:\n"
                         f"• ID: {rent.user_id}\n"
                         f"• Username: @{rent.username or 'не указан'}\n"
                         f"• Имя: {rent.first_name or ''} {rent.last_name or ''}\n\n"
                         f"📅 Окончание: {rent.end_date.strftime('%d.%m.%Y %H:%M')}\n"
                         f"⏳ Осталось дней: {days_left}\n"
                         f"💰 Оплачено месяцев: {rent.months}",
                    parse_mode="HTML"
                )
                logger.info(f"Отправлено уведомление админу об истечении аренды пользователя {rent.user_id}")
            except Exception as e:
                logger.error(f"Не удалось отправить уведомление админу: {e}")

        # Получаем просроченные аренды
        expired_rents = get_expired_rents()

        for rent in expired_rents:
            # Деактивируем аренду
            deactivate_server_rent(rent.id)

            # Отправляем уведомление пользователю
            try:
                await bot.send_message(
                    chat_id=rent.user_id,
                    text=f"❌ <b>Аренда сервера истекла!</b>\n\n"
                         f"📅 Ваша аренда сервера истекла {rent.end_date.strftime('%d.%m.%Y %H:%M')}.\n\n"
                         f"Доступ к серверу прекращен.\n\n"
                         f"Для продления аренды обратитесь к @PyAdminRU",
                    parse_mode="HTML"
                )
                logger.info(f"Отправлено уведомление пользователю {rent.user_id} об истечении аренды")
            except Exception as e:
                logger.error(f"Не удалось отправить уведомление пользователю {rent.user_id}: {e}")

            # Отправляем уведомление админу
            try:
                await bot.send_message(
                    chat_id=ADMIN_CHAT_ID,
                    text=f"❌ <b>Аренда сервера истекла!</b>\n\n"
                         f"👤 Пользователь:\n"
                         f"• ID: {rent.user_id}\n"
                         f"• Username: @{rent.username or 'не указан'}\n\n"
                         f"📅 Окончание: {rent.end_date.strftime('%d.%m.%Y %H:%M')}\n\n"
                         f"Аренда деактивирована.",
                    parse_mode="HTML"
                )
                logger.info(f"Деактивирована аренда пользователя {rent.user_id}")
            except Exception as e:
                logger.error(f"Не удалось отправить уведомление админу: {e}")

        if expiring_rents or expired_rents:
            logger.info(f"Проверка завершена. Истекающих: {len(expiring_rents)}, Истекших: {len(expired_rents)}")
        else:
            logger.info("Проверка завершена. Нет истекающих или истекших аренд.")

    except Exception as e:
        logger.exception(f"Ошибка при проверке сроков аренды: {e}")


async def run_periodic_check(interval_hours: int = 24):
    """
    Запускает периодическую проверку сроков аренды
    :param interval_hours: интервал проверки в часах
    """
    logger.info(f"Запуск периодической проверки аренды сервера (интервал: {interval_hours} ч.)")

    while True:
        await check_server_rent_expiration()
        await asyncio.sleep(interval_hours * 60 * 60)  # Конвертируем часы в секунды


if __name__ == "__main__":
    # Для тестирования
    asyncio.run(check_server_rent_expiration())
