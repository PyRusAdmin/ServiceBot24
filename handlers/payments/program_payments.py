import datetime  # Дата

from aiogram import types, F
from aiogram.fsm.context import FSMContext

from handlers.payments.products_goods_services import TelegramMaster
from keyboards.payments_keyboards import payment_keyboard
from system.dispatcher import bot, dp


@dp.callback_query(F.data == "delivery")
async def buy(callback_query: types.CallbackQuery, state: FSMContext):
    """Покупка TelegramMaster 2.0"""

    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    payment_keyboard_key = payment_keyboard()
    payment_mes = ("Купить TelegramMaster 2.0. \n\n"
                   f"Цена на {current_date} — {TelegramMaster} рублей.\n\n"
                   "Если по какой-либо причине бот не выдал пароль или произошла ошибка платежа, писать: "
                   "@PyAdminRU. 🤖🔒\n\n"
                   "Для возврата в начальное меню, нажмите: /start")
    await bot.send_message(callback_query.message.chat.id, payment_mes, reply_markup=payment_keyboard_key)


def register_program_payments():
    """Регистрируем handlers для бота"""
    dp.message.register(buy)
