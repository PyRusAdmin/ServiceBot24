# -*- coding: utf-8 -*-
import datetime  # Дата
import json
import uuid

from aiogram import F, Router, types
from aiogram.types import FSInputFile
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from loguru import logger  # Логирование с помощью loguru

from db.settings_db import save_payment_info, add_user_if_not_exists, is_user_in_db
from handlers.payments.cryptomus_payments.cryptomus_commentator import make_request
from handlers.payments.products_goods_services import password_TelegramMaster_Commentator, password_TelegramMaster
from keyboards.user_keyboards import start_menu
from system.dispatcher import bot

router = Router(name=__name__)

# Обработчик для создания счета и отправки кнопки "Проверить оплату"
@router.callback_query(F.data == "payment_crypta_commentator_pass")
async def buy_handler_commentator(callback_query: types.CallbackQuery):
    """Оплата пароля TelegramMaster_Commentator криптой"""

    # Создаем счет для оплаты
    invoice_data = await make_request(
        url="https://api.cryptomus.com/v1/payment",
        invoice_data={
            "amount": f"{password_TelegramMaster}",
            "currency": "RUB",
            "order_id": str(uuid.uuid4())
        },
    )
    logger.info(f"Счет для оплаты криптовалютой: {invoice_data}")
    # Создаем кнопку "Проверить оплату"
    check_payment_button = InlineKeyboardButton(
        text="Проверить оплату",
        callback_data=f"check_paymentPass_{invoice_data['result']['uuid']}"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[check_payment_button]])

    # Отправляем сообщение с кнопкой
    await bot.send_message(
        chat_id=callback_query.message.chat.id,
        text=f"💳 <b>Счет для оплаты криптовалютой</b> 💳\n\n"
             f"🌐 Вы собираетесь получить пароль от <b>TelegramMaster_Commentator</b>. Пожалуйста, воспользуйтесь ссылкой ниже для оплаты:\n"
             f"🔗 <a href='{invoice_data['result']['url']}'>Перейти к оплате</a>\n\n"
             f"⚠️ <b>Важная информация:</b> после завершения платежа нажмите кнопку 'Проверить оплату'.\n"
             f"❗️ Обратите внимание, что возврат денежных средств после оплаты криптовалютой невозможен.\n\n"
             f"💡 Если у вас возникнут вопросы, не стесняйтесь обращаться к нам. Спасибо за доверие! 🙌",
        reply_markup=keyboard,
        parse_mode="HTML"
    )


# Обработчик для кнопки "Проверить оплату"
@router.callback_query(F.data.startswith("check_paymentPass_"))
async def check_payment_handler_commentator(callback_query: types.CallbackQuery):
    """Ручная проверка статуса оплаты"""
    invoice_uuid = callback_query.data.split("_")[2]  # Извлекаем UUID счета из callback_data
    logger.info(f"Проверка статуса оплаты по UUID: {invoice_uuid}")
    # Проверяем статус оплаты
    try:
        invoice_data = await make_request(
            url="https://api.cryptomus.com/v1/payment/info",
            invoice_data={"uuid": invoice_uuid},
        )

        if invoice_data['result']['payment_status'] in ('paid', 'paid_over'):
            # Если оплата прошла успешно
            date = datetime.datetime.now().strftime("%Y-%m-%d")
            invoice_json = json.dumps(invoice_data)  # Преобразуем словарь в строку JSON

            # Запись в базу данных пользователя, который оплатил счет в крипте
            save_payment_info(callback_query.from_user.id, callback_query.from_user.first_name,
                              callback_query.from_user.last_name, callback_query.from_user.username, invoice_json,
                              "Пароль обновления: TelegramMaster_Commentator", date, "succeeded")
            # Отправляем файл и сообщение об успешной оплате
            caption = (f"Платеж на сумму {password_TelegramMaster_Commentator} руб прошел успешно‼️ \n\n"
                       f"Вы можете скачать программу  TelegramMaster_Commentator\n\n"
                       f"Для возврата в начальное меню нажмите /start")
            await bot.send_document(chat_id=callback_query.from_user.id,
                                    document=FSInputFile("setting/password/TelegramMaster_Commentator/password.txt"),
                                    caption=caption,
                                    reply_markup=start_menu()  # Отправляемся в главное меню
                                    )
            # Проверяем наличие пользователя в базе данных
            result = is_user_in_db(callback_query.from_user.id)
            if result is None:
                add_user_if_not_exists(callback_query.from_user.id)
                await bot.send_message(chat_id=ADMIN_CHAT_ID, text=f"Пользователь:\n"
                                                                   f"ID {callback_query.from_user.id},\n"
                                                                   f"Username: @{callback_query.from_user.username},\n"
                                                                   f"Имя: {callback_query.from_user.first_name},\n"
                                                                   f"Фамилия: {callback_query.from_user.last_name},\n\n"
                                                                   f"Приобрел пароль от TelegramMaster_Commentator (криптой)")
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



