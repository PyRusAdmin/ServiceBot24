import datetime  # Дата

from aiogram import types, F

from handlers.payments.products_goods_services import TelegramMaster, payment_installation
from keyboards.payments_keyboards import payment_keyboard
from keyboards.payments_keyboards import purchasing_a_program_setup_service
from system.dispatcher import bot, dp


@dp.callback_query(F.data == "delivery")
async def buy(callback_query: types.CallbackQuery):
    """Покупка TelegramMaster 2.0"""
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    payment_keyboard_key = payment_keyboard()
    payment_mes = ("Купить TelegramMaster 2.0. \n\n"
                   f"Цена на {current_date} — {TelegramMaster} рублей.\n\n"
                   "Если по какой-либо причине бот не выдал пароль или произошла ошибка платежа, писать: "
                   "@PyAdminRU. 🤖🔒\n\n"
                   "Для возврата в начальное меню, нажмите: /start")
    await bot.send_message(callback_query.message.chat.id, payment_mes, reply_markup=payment_keyboard_key)


@dp.callback_query(F.data == "purchasing_a_program_setup_service")
async def buy_program_setup_service(callback_query: types.CallbackQuery):
    """Оплата услуг по установке ПО"""
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    payment_keyboard_key = purchasing_a_program_setup_service()
    payment_mes = ("Оплатите услуги по настройке и консультации.\n\n"
                   f"Цена на {current_date} — {payment_installation} рублей.\n\n"
                   "После завершения процесса оплаты, свяжитесь с администратором через личные сообщения, используя "
                   "указанный никнейм: @PyAdminRU. 🤖🔒\n\n"
                   "Для возврата в начальное меню, нажмите: /start")
    await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                message_id=callback_query.message.message_id,
                                text=payment_mes,
                                reply_markup=payment_keyboard_key,
                                disable_web_page_preview=True)


def register_program_payments():
    """Регистрируем handlers для бота"""
    dp.message.register(buy)
    dp.message.register(buy_program_setup_service)
