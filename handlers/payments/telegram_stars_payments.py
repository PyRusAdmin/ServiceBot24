# -*- coding: utf-8 -*-
"""
Оплата через Telegram Stars (звезды)
Курс звезд обновляется динамически
Актуальный курс: ~1 звезда = 1.5 рубля (может меняться)
"""
import datetime
import json

from aiogram import F, Router, types
from loguru import logger

from db.settings_db import save_payment_info, get_product_password

from handlers.payments.products_goods_services import (
    TelegramMaster_PRO, TelegramMaster_Commentator, payment_installation, TelegramMaster_Search_GPT, get_stars_amount
)
from messages.messages import message_check_payment
from system.dispatcher import bot, ADMIN_CHAT_ID

router = Router(name=__name__)

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
            price = TelegramMaster_PRO
        elif payload.startswith("stars_com_"):
            product_name = "TelegramMaster_Commentator"
            price = TelegramMaster_Commentator
        elif payload.startswith("stars_pass_"):
            product_name = "TelegramMaster-PRO"  # Пароль для TelegramMaster-PRO
            price = TelegramMaster_PRO.get("price_password")
        elif payload.startswith("stars_com_pass_"):
            product_name = "TelegramMaster_Commentator"  # Пароль для TelegramMaster_Commentator
            price = TelegramMaster_Commentator.get("price_password")
        elif payload.startswith("stars_training_"):
            product_name = "Настройка ПО"
            price = payment_installation
        elif payload.startswith("stars_search_"):
            product_name = "TelegramMaster_Search_GPT"
            price = TelegramMaster_Search_GPT
        else:
            await message.answer("⚠️ Неизвестный тип платежа. Обратитесь к @PyAdminRU")
            return

        # Проверяем, нужен ли пароль для этого продукта
        needs_password = not payload.startswith("stars_training_")

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
        if needs_password:
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
    stars_amount = get_stars_amount(TelegramMaster_PRO)

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
    stars_amount = get_stars_amount(TelegramMaster_Commentator)

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
    stars_amount = get_stars_amount(TelegramMaster_PRO.get())

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
    stars_amount = get_stars_amount(TelegramMaster_Commentator.get("price_password"))

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
    stars_amount = get_stars_amount(payment_installation)

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
