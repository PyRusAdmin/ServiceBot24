# -*- coding: utf-8 -*-
"""
Оплата через Telegram Stars (звезды)
Курс звезд обновляется динамически
Актуальный курс: ~1 звезда = 1.5 рубля (может меняться)
"""
import datetime
import json
import os

from aiogram import F, Router, types
from aiogram.types import FSInputFile
from loguru import logger

from db.settings_db import save_payment_info, get_product_password
from handlers.payments.products_goods_services import (
    TelegramMaster, TelegramMaster_Commentator, password_TelegramMaster,
    password_TelegramMaster_Commentator, payment_installation, TelegramMaster_Search_GPT
)
from keyboards.user_keyboards import start_menu
from messages.messages import message_check_payment
from system.dispatcher import bot, ADMIN_CHAT_ID

router = Router(name=__name__)

# Курс Telegram Stars (рублей за 1 звезду)
# Обновите это значение при изменении курса Telegram
# Актуальный курс на 2026 год: ~1.5 рубля за звезду
STARS_TO_RUB_RATE = 200

# Базовый путь к файлам с паролями
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def get_stars_amount(rub_amount: float) -> int:
    """
    Конвертирует сумму из рублей в звезды Telegram
    :param rub_amount: сумма в рублях
    :return: количество звезд (целое число)
    """
    stars = int(rub_amount / STARS_TO_RUB_RATE)
    # Округляем до ближайшего значения, которое принимает Telegram (минимум 50 звезд)
    stars = max(1, stars)
    return stars


# Словарь для хранения ожидающих платежей
pending_stars_payments = {}


@router.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    """Обработка предоплаченного инвойса"""
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@router.message(F.successful_payment)
async def process_successful_payment(message: types.Message):
    """Обработка успешной оплаты звездами"""
    try:
        payment_data = message.successful_payment
        payload = payment_data.invoice_payload

        logger.info(f"Успешная оплата звездами: {payload}, сумма: {payment_data.total_amount} звезд")

        # Определяем продукт по payload
        if payload.startswith("stars_program_"):
            product_name = "TelegramMaster-PRO"
            price = TelegramMaster
            password_file = "setting/password/TelegramMaster-PRO/password.txt"
        elif payload.startswith("stars_com_"):
            product_name = "TelegramMaster_Commentator"
            price = TelegramMaster_Commentator
            password_file = "setting/password/TelegramMaster_Commentator/password.txt"
        elif payload.startswith("stars_pass_"):
            product_name = "Пароль TelegramMaster-PRO"
            price = password_TelegramMaster
            password_file = "setting/password/TelegramMaster-PRO/password.txt"
        elif payload.startswith("stars_com_pass_"):
            product_name = "Пароль TelegramMaster_Commentator"
            price = password_TelegramMaster_Commentator
            password_file = "setting/password/TelegramMaster_Commentator/password.txt"
        elif payload.startswith("stars_training_"):
            product_name = "Настройка ПО"
            price = payment_installation
            password_file = None
        elif payload.startswith("stars_search_"):
            product_name = "TelegramMaster_Search_GPT"
            price = TelegramMaster_Search_GPT
            password_file = "setting/password/TelegramMaster_Search_GPT/password.txt"
        else:
            await message.answer("⚠️ Неизвестный тип платежа. Обратитесь к @PyAdminRU")
            return

        logger.info(f"Путь к файлу с паролем: {password_file}")
        logger.info(f"Файл существует: {os.path.exists(password_file)}")

        # Сохраняем информацию о платеже
        invoice_json = json.dumps({
            "product": product_name,
            "amount_stars": payment_data.total_amount,
            "date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "status": "succeeded",
            "user_id": message.from_user.id
        })

        save_payment_info(
            user_id=message.from_user.id,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            username=message.from_user.username,
            invoice_json=invoice_json,
            product=product_name,
            date=datetime.datetime.now().strftime("%Y-%m-%d"),
            status="succeeded"
        )

        # Получаем пароль из базы данных и отправляем пользователю
        if password_file:
            try:
                password = get_product_password(product_name)
                
                if password:
                    await bot.send_message(
                        chat_id=message.from_user.id,
                        text=f"✅ <b>Оплата подтверждена!</b>\n\n"
                             f"📦 Продукт: <b>{product_name}</b>\n\n"
                             f"🔑 <b>Ваш пароль:</b>\n"
                             f"<code>{password}</code>\n\n"
                             f"{message_check_payment(product_price=price, product=product_name)}",
                        parse_mode="HTML"
                    )
                    logger.info(f"Пароль отправлен пользователю {message.from_user.id}")
                else:
                    # Пароль не найден в БД
                    await bot.send_message(
                        chat_id=message.from_user.id,
                        text=f"⚠️ <b>Внимание!</b>\n\n"
                             f"Оплата прошла успешно, но пароль для '{product_name}' еще не установлен администратором.\n\n"
                             f"Пожалуйста, обратитесь к @PyAdminRU",
                        parse_mode="HTML"
                    )
                    logger.warning(f"Пароль для {product_name} не найден в базе данных")
            except Exception as send_error:
                logger.exception(f"Ошибка при отправке пароля: {send_error}")
                await message.answer("⚠️ Ошибка при отправке пароля. Обратитесь к @PyAdminRU")
        else:
            await message.answer(
                f"✅ <b>Оплата услуги '{product_name}' подтверждена!</b>\n\n"
                f"Пожалуйста, свяжитесь с @PyAdminRU для начала работы.",
                parse_mode="HTML"
            )

        # Уведомляем администратора
        await bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=f"⭐️ <b>Новая оплата звездами!</b>\n\n"
                 f"👤 Пользователь:\n"
                 f"• ID: {message.from_user.id}\n"
                 f"• Username: @{message.from_user.username}\n"
                 f"• Имя: {message.from_user.first_name}\n"
                 f"• Фамилия: {message.from_user.last_name}\n\n"
                 f"📦 Продукт: {product_name}\n"
                 f"💰 Сумма: {payment_data.total_amount} ⭐️ ({price} ₽)\n"
                 f"🕒 Дата: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            parse_mode="HTML"
        )

        logger.info(f"Оплата звездами обработана: {product_name}, пользователь {message.from_user.id}")

    except Exception as e:
        logger.exception(f"Ошибка при обработке успешной оплаты звездами: {e}")
        await message.answer("⚠️ Произошла ошибка при обработке платежа. Обратитесь к @PyAdminRU")


# ============================================================================
# TelegramMaster-PRO оплата звездами
# ============================================================================

@router.callback_query(F.data == "payment_stars_program")
async def payment_stars_program_handler(callback_query: types.CallbackQuery):
    """Оплата TelegramMaster-PRO звездами"""
    rub_price = TelegramMaster
    stars_amount = get_stars_amount(rub_price)

    try:
        await bot.send_invoice(
            chat_id=callback_query.message.chat.id,
            title="TelegramMaster-PRO",
            description="Лицензия TelegramMaster-PRO с полным функционалом",
            payload=f"stars_program_{datetime.datetime.now().timestamp()}",
            provider_token="",
            currency="XTR",
            prices=[types.LabeledPrice(label="TelegramMaster-PRO", amount=stars_amount)],
            start_parameter="stars_program",
            need_name=False,
            need_email=False,
            need_phone_number=False,
            need_shipping_address=False,
            send_phone_number_to_provider=False,
            send_email_to_provider=False,
        )

        logger.info(
            f"Создан инвойс для TelegramMaster-PRO: {stars_amount} звезд, пользователь {callback_query.from_user.id}")

    except Exception as e:
        logger.exception(f"Ошибка при создании инвойса TelegramMaster-PRO: {e}")
        await bot.send_message(
            chat_id=callback_query.message.chat.id,
            text="⚠️ Произошла ошибка при создании платежа. Пожалуйста, попробуйте позже."
        )


# ============================================================================
# TelegramMaster_Commentator оплата звездами
# ============================================================================

@router.callback_query(F.data == "payment_stars_commentator")
async def payment_stars_commentator_handler(callback_query: types.CallbackQuery):
    """Оплата TelegramMaster_Commentator звездами"""
    rub_price = TelegramMaster_Commentator
    stars_amount = get_stars_amount(rub_price)

    try:
        await bot.send_invoice(
            chat_id=callback_query.message.chat.id,
            title="TelegramMaster_Commentator",
            description="Лицензия TelegramMaster_Commentator",
            payload=f"stars_com_{datetime.datetime.now().timestamp()}",
            provider_token="",
            currency="XTR",
            prices=[types.LabeledPrice(label="TelegramMaster_Commentator", amount=stars_amount)],
            start_parameter="stars_com",
            need_name=False,
            need_email=False,
            need_phone_number=False,
            need_shipping_address=False,
            send_phone_number_to_provider=False,
            send_email_to_provider=False,
        )

        logger.info(
            f"Создан инвойс для TelegramMaster_Commentator: {stars_amount} звезд, пользователь {callback_query.from_user.id}")

    except Exception as e:
        logger.exception(f"Ошибка при создании инвойса TelegramMaster_Commentator: {e}")
        await bot.send_message(
            chat_id=callback_query.message.chat.id,
            text="⚠️ Произошла ошибка при создании платежа. Пожалуйста, попробуйте позже."
        )


@router.callback_query(F.data == "payment_stars_password")
async def payment_stars_password_handler(callback_query: types.CallbackQuery):
    """Оплата пароля TelegramMaster-PRO звездами"""
    rub_price = password_TelegramMaster
    stars_amount = get_stars_amount(rub_price)

    try:
        await bot.send_invoice(
            chat_id=callback_query.message.chat.id,
            title="Пароль TelegramMaster-PRO",
            description="Пароль для доступа к TelegramMaster-PRO",
            payload=f"stars_pass_{datetime.datetime.now().timestamp()}",
            provider_token="",
            currency="XTR",
            prices=[types.LabeledPrice(label="Пароль TelegramMaster-PRO", amount=stars_amount)],
            start_parameter="stars_pass",
            need_name=False,
            need_email=False,
            need_phone_number=False,
            need_shipping_address=False,
            send_phone_number_to_provider=False,
            send_email_to_provider=False,
        )

        logger.info(
            f"Создан инвойс для пароля TelegramMaster-PRO: {stars_amount} звезд, пользователь {callback_query.from_user.id}")

    except Exception as e:
        logger.exception(f"Ошибка при создании инвойса пароля TelegramMaster-PRO: {e}")
        await bot.send_message(
            chat_id=callback_query.message.chat.id,
            text="⚠️ Произошла ошибка при создании платежа. Пожалуйста, попробуйте позже."
        )


@router.callback_query(F.data == "payment_stars_commentator_password")
async def payment_stars_commentator_password_handler(callback_query: types.CallbackQuery):
    """Оплата пароля TelegramMaster_Commentator звездами"""
    rub_price = password_TelegramMaster_Commentator
    stars_amount = get_stars_amount(rub_price)

    try:
        await bot.send_invoice(
            chat_id=callback_query.message.chat.id,
            title="Пароль TelegramMaster_Commentator",
            description="Пароль для доступа к TelegramMaster_Commentator",
            payload=f"stars_com_pass_{datetime.datetime.now().timestamp()}",
            provider_token="",
            currency="XTR",
            prices=[types.LabeledPrice(label="Пароль TelegramMaster_Commentator", amount=stars_amount)],
            start_parameter="stars_com_pass",
            need_name=False,
            need_email=False,
            need_phone_number=False,
            need_shipping_address=False,
            send_phone_number_to_provider=False,
            send_email_to_provider=False,
        )

        logger.info(
            f"Создан инвойс для пароля TelegramMaster_Commentator: {stars_amount} звезд, пользователь {callback_query.from_user.id}")

    except Exception as e:
        logger.exception(f"Ошибка при создании инвойса пароля TelegramMaster_Commentator: {e}")
        await bot.send_message(
            chat_id=callback_query.message.chat.id,
            text="⚠️ Произошла ошибка при создании платежа. Пожалуйста, попробуйте позже."
        )


@router.callback_query(F.data == "payment_stars_training")
async def payment_stars_training_handler(callback_query: types.CallbackQuery):
    """Оплата настройки ПО звездами"""
    rub_price = payment_installation
    stars_amount = get_stars_amount(rub_price)

    try:
        await bot.send_invoice(
            chat_id=callback_query.message.chat.id,
            title="Настройка ПО",
            description="Услуги по настройке и консультации ПО",
            payload=f"stars_training_{datetime.datetime.now().timestamp()}",
            provider_token="",
            currency="XTR",
            prices=[types.LabeledPrice(label="Настройка ПО", amount=stars_amount)],
            start_parameter="stars_training",
            need_name=False,
            need_email=False,
            need_phone_number=False,
            need_shipping_address=False,
            send_phone_number_to_provider=False,
            send_email_to_provider=False,
        )

        logger.info(f"Создан инвойс для настройки ПО: {stars_amount} звезд, пользователь {callback_query.from_user.id}")

    except Exception as e:
        logger.exception(f"Ошибка при создании инвойса настройки ПО: {e}")
        await bot.send_message(
            chat_id=callback_query.message.chat.id,
            text="⚠️ Произошла ошибка при создании платежа. Пожалуйста, попробуйте позже."
        )


@router.callback_query(F.data == "payment_stars_search_gpt")
async def payment_stars_search_gpt_handler(callback_query: types.CallbackQuery):
    """Оплата TelegramMaster_Search_GPT звездами"""
    rub_price = TelegramMaster_Search_GPT
    stars_amount = get_stars_amount(rub_price)

    try:
        await bot.send_invoice(
            chat_id=callback_query.message.chat.id,
            title="TelegramMaster_Search_GPT",
            description="Лицензия TelegramMaster_Search_GPT",
            payload=f"stars_search_{datetime.datetime.now().timestamp()}",
            provider_token="",
            currency="XTR",
            prices=[types.LabeledPrice(label="TelegramMaster_Search_GPT", amount=stars_amount)],
            start_parameter="stars_search",
            need_name=False,
            need_email=False,
            need_phone_number=False,
            need_shipping_address=False,
            send_phone_number_to_provider=False,
            send_email_to_provider=False,
        )

        logger.info(
            f"Создан инвойс для TelegramMaster_Search_GPT: {stars_amount} звезд, пользователь {callback_query.from_user.id}")

    except Exception as e:
        logger.exception(f"Ошибка при создании инвойса TelegramMaster_Search_GPT: {e}")
        await bot.send_message(
            chat_id=callback_query.message.chat.id,
            text="⚠️ Произошла ошибка при создании платежа. Пожалуйста, попробуйте позже."
        )
