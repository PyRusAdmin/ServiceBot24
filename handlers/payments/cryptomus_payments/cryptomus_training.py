# -*- coding: utf-8 -*-
import datetime  # Дата
import json
import uuid

from aiogram import types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from loguru import logger  # Логирование с помощью loguru
from aiogram import F, Router, types
from db.settings_db import save_payment_info
from handlers.payments.cryptomus_payments.cryptomus_commentator import make_request
from handlers.payments.products_goods_services import payment_installation
from system.dispatcher import bot, dp, ADMIN_CHAT_ID

router = Router(name=__name__)

@dp.callback_query(F.data == "payment_crypta_pas_training_handler")
async def payment_crypta_pas_training_handler(callback_query: types.CallbackQuery):
    """Оплата установки и обучения криптой"""

    invoice_data = await make_request(
        url="https://api.cryptomus.com/v1/payment",
        invoice_data={
            "amount": f"{payment_installation}",
            "currency": "RUB",
            "order_id": str(uuid.uuid4())
        },
    )

    logger.info(f"Счет для оплаты криптовалютой: {invoice_data}")
    # Создаем кнопку "Проверить оплату"
    check_payment_button = InlineKeyboardButton(
        text="Проверить оплату",
        callback_data=f"check_paymentT_{invoice_data['result']['uuid']}"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[check_payment_button]])

    await bot.send_message(chat_id=callback_query.message.chat.id,
                           text=f"💳 <b>Счет для оплаты криптовалютой</b> 💳\n\n"
                                f"🌐 Вы собираетесь приобрести <b>Помощь в настройке ПО (консультация)</b>. Пожалуйста, воспользуйтесь ссылкой ниже для оплаты:\n"
                                f"🔗 <a href='{invoice_data['result']['url']}'>Перейти к оплате</a>\n\n"
                                f"⚠️ <b>Важная информация:</b> после завершения платежа бот автоматически отправит вам все необходимые данные.\n"
                                f"❗️ Обратите внимание, что возврат денежных средств после оплаты криптовалютой невозможен.\n\n"
                                f"💡 Если у вас возникнут вопросы, не стесняйтесь обращаться к нам. Спасибо за доверие! 🙌",
                           reply_markup=keyboard,
                           parse_mode="HTML")


# Обработчик для кнопки "Проверить оплату"
@dp.callback_query(F.data.startswith("check_paymentT_"))
async def check_invoice_paid_training(callback_query: types.CallbackQuery):
    """Проверка счета на оплаченность"""
    invoice_uuid = callback_query.data.split("_")[2]  # Извлекаем UUID счета из callback_data
    logger.info(f"Проверка статуса оплаты по UUID: {invoice_uuid}")
    # Проверяем статус оплаты
    try:
        invoice_data = await make_request(
            url="https://api.cryptomus.com/v1/payment/info",
            invoice_data={"uuid": id},
        )
        if invoice_data['result']['payment_status'] in ('paid', 'paid_over'):
            date = datetime.datetime.now().strftime("%Y-%m-%d")
            invoice_json = json.dumps(invoice_data)  # Преобразуем словарь в строку JSON
            # Запись в базу данных пользователя, который оплатил счет в крипте
            save_payment_info(callback_query.from_user.id, callback_query.from_user.first_name,
                              callback_query.from_user.last_name, callback_query.from_user.username, invoice_json,
                              "Помощь в настройке ПО (консультация)", date, "succeeded")
            await bot.send_message(callback_query.from_user.id,
                                   "Оплата прошла успешно‼️ \nДля согласования даты и времени , свяжитесь с администратором"
                                   " через личные сообщения, используя указанный никнейм: @PyAdminRU. 🤖🔒\n\n"
                                   "Для возврата в начальное меню, нажмите: /start")
            await bot.send_message(chat_id=ADMIN_CHAT_ID, text=f"Пользователь:\n"
                                                               f"ID {callback_query.from_user.id},\n"
                                                               f"Username: @{callback_query.from_user.username},\n"
                                                               f"Имя: {callback_query.from_user.first_name},\n"
                                                               f"Фамилия: {callback_query.from_user.last_name},\n\n"
                                                               f"Приобрел 'Помощь в настройке ПО (консультация)' (криптой)")
        else:
            # Если оплата еще не прошла
            await bot.send_message(
                chat_id=callback_query.message.chat.id,
                text="❌ Платеж еще не оплачен. Пожалуйста, завершите оплату и нажмите кнопку 'Проверить оплату' еще раз."
            )
    except Exception as e:
        # Обработка ошибок
        logger.error(f"Ошибка при проверке оплаты: {e}")
        await bot.send_message(
            chat_id=callback_query.message.chat.id,
            text="⚠️ Произошла ошибка при проверке оплаты. Пожалуйста, попробуйте позже."
        )


def register_cryptomus_training():
    """Регистрируем handlers для бота"""
    dp.message.register(payment_crypta_pas_training_handler)
