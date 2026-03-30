# -*- coding: utf-8 -*-
from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from loguru import logger  # Логирование с помощью loguru
from yookassa import Payment

from db.settings_db import save_payment_info
from handlers.payment_yookassa import payment_yookassa_com
from handlers.payments.products_goods_services import payment_installation
from keyboards.payments_keyboards import payment_yookassa_check_keyboard_custom
from messages.messages import message_payment
from services.i18n import t
from system.dispatcher import bot, ADMIN_CHAT_ID

router = Router(name=__name__)


@router.callback_query(F.data.startswith("payment_yookassa_training"))
async def payment_url_handler(callback_query: types.CallbackQuery):
    """Отправка ссылки для оплаты TelegramMaster-PRO"""
    payment_url, payment_id = payment_yookassa_com(
        description_text=f"Помощь в настройке ПО (консультация)",  # Текст описания товара
        product_price=payment_installation  # Цена товара в рублях
    )
    await bot.send_message(
        chat_id=callback_query.from_user.id,
        text=message_payment(
            "Помощь в настройке ПО (консультация)",
            payment_url
        ),
        reply_markup=payment_yookassa_check_keyboard_custom(
            # Создаем клавиатуру с кнопкой для проверки оплаты и возврата в меню
            payment_id,
            "csheck_service"
        ),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("csheck_service"))
async def check_payment_program_setup_service(callback_query: types.CallbackQuery, state: FSMContext):
    split_data = callback_query.data.split("_")
    logger.info(split_data[2])
    # Проверьте статус платежа с помощью API yookassa
    payment_info = Payment.find_one(split_data[2])
    logger.info(payment_info)
    if payment_info.status == "succeeded":  # Обработка статуса платежа
        # Запись в базу данных пользователя, который оплатил счет в рублях
        save_payment_info(
            callback_query.from_user.id,
            callback_query.from_user.first_name,
            callback_query.from_user.last_name,
            callback_query.from_user.username,
            payment_info.id,
            "Помощь в настройке ПО (консультация)",
            payment_info.captured_at,
            "succeeded"
        )
        await bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=f"Пользователь:\n"
                 f"ID {callback_query.from_user.id},\n"
                 f"Username: @{callback_query.from_user.username},\n"
                 f"Имя: {callback_query.from_user.first_name},\n"
                 f"Фамилия: {callback_query.from_user.last_name},\n\n"
                 f"Приобрел 'Помощь в настройке ПО (консультация)'"
        )
        await bot.send_message(
            chat_id=callback_query.from_user.id,
            text=t("training-payment-success")
        )
    else:
        await bot.send_message(
            callback_query.message.chat.id,
            text=t("payment-not-completed")
        )
