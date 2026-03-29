# -*- coding: utf-8 -*-
"""
Обработчики оплаты аренды сервера через Telegram Stars
"""
import datetime

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from loguru import logger

from db.settings_db import add_server_rent, get_active_server_rent
from handlers.payments.products_goods_services import SERVER_RENT_PRICE
from handlers.payments.telegram_stars_payments import get_stars_amount
from keyboards.user_keyboards import start_menu
from states.states import ServerRentStarsState
from system.dispatcher import bot, ADMIN_CHAT_ID

router = Router(name=__name__)

product = "Аренда сервера"


@router.callback_query(F.data == "payment_stars_server_rent")
async def server_rent_stars_handler(callback_query: types.CallbackQuery, state: FSMContext):
    """Выбор количества месяцев для аренды сервера через Stars"""

    # Проверяем, есть ли активная аренда
    active_rent = get_active_server_rent(callback_query.from_user.id)
    if active_rent:
        await bot.send_message(
            chat_id=callback_query.from_user.id,
            text=f"⚠️ <b>У вас уже есть активная аренда сервера!</b>\n\n"
                 f"📅 Дата окончания: {active_rent.end_date.strftime('%d.%m.%Y %H:%M')}\n"
                 f"💰 Оплачено месяцев: {active_rent.months}\n\n"
                 f"Дождитесь окончания текущей аренды или обратитесь к @PyAdminRU",
            reply_markup=start_menu(),
            parse_mode="HTML"
        )
        await callback_query.answer()
        return

    # Рассчитываем стоимость в звездах для каждого срока
    months_options = [1, 2, 3, 6, 12]
    keyboard_buttons = []
    
    for months in months_options:
        rub_price = SERVER_RENT_PRICE * months
        stars_price = get_stars_amount(rub_price)
        month_word = "месяц" if months == 1 else "месяца" if months < 5 else "месяцев"
        keyboard_buttons.append([
            InlineKeyboardButton(
                text=f"{months} {month_word} - {rub_price} ₽ ({stars_price} ⭐️)",
                callback_data=f"stars_rent_{months}_month"
            )
        ])
    
    keyboard_buttons.append([InlineKeyboardButton(text="🏠 В главное меню", callback_data="start_menu_keyboard")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

    await bot.send_message(
        chat_id=callback_query.from_user.id,
        text="⭐️ <b>Аренда сервера за Stars</b>\n\n"
             "Выберите срок аренды сервера:\n\n"
             "💰 <b>Цена:</b> 250 ₽/месяц (~167 ⭐️)\n"
             "⚡️ <b>Скидки:</b>\n"
             "• 6 месяцев - 1500 ₽ (~1000 ⭐️)\n"
             "• 12 месяцев - 3000 ₽ (~2000 ⭐️)\n\n"
             "📡 Сервер будет доступен 24/7 для ваших задач",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback_query.answer()


@router.callback_query(F.data.startswith("stars_rent_"))
async def select_months_stars_handler(callback_query: types.CallbackQuery, state: FSMContext):
    """Обработчик выбора количества месяцев для Stars"""
    # Извлекаем количество месяцев из callback_data
    try:
        months = int(callback_query.data.split("_")[3])
    except (IndexError, ValueError):
        await callback_query.answer("❌ Ошибка выбора срока аренды", show_alert=True)
        return
    
    rub_price = SERVER_RENT_PRICE * months
    stars_amount = get_stars_amount(rub_price)

    # Сохраняем выбранные месяцы в состоянии
    await state.update_data(months=months, rub_price=rub_price, stars_amount=stars_amount)
    await state.set_state(ServerRentStarsState.waiting_for_payment)

    try:
        await bot.send_invoice(
            chat_id=callback_query.message.chat.id,
            title=f"Аренда сервера ({months} мес.)",
            description=f"Аренда сервера на {months} {'месяц' if months == 1 else 'месяца' if months < 5 else 'месяцев'}",
            payload=f"stars_server_rent_{months}_{datetime.datetime.now().timestamp()}",
            provider_token="",
            currency="XTR",
            prices=[types.LabeledPrice(label=f"Аренда сервера ({months} мес.)", amount=stars_amount)],
            start_parameter=f"stars_rent_{months}",
            need_name=False,
            need_email=False,
            need_phone_number=False,
            need_shipping_address=False,
            send_phone_number_to_provider=False,
            send_email_to_provider=False,
        )

        logger.info(f"Создан инвойс для аренды сервера: {months} мес., {stars_amount} звезд")

    except Exception as e:
        logger.exception(f"Ошибка при создании инвойса аренды сервера: {e}")
        await bot.send_message(
            chat_id=callback_query.from_user.id,
            text="⚠️ Произошла ошибка при создании платежа. Пожалуйста, попробуйте позже."
        )
        await state.clear()

    await callback_query.answer()


@router.pre_checkout_query(F.data.source.startswith("stars_rent_"))
async def process_pre_checkout_query_server_rent(pre_checkout_query: types.PreCheckoutQuery):
    """Обработка предоплаченного инвойса аренды сервера"""
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@router.message(F.successful_payment)
async def process_successful_payment_server_rent(message: types.Message, state: FSMContext):
    """Обработка успешной оплаты аренды сервера звездами"""
    try:
        payment_data = message.successful_payment
        payload = payment_data.invoice_payload

        # Проверяем, что это оплата аренды сервера
        if not payload.startswith("stars_server_rent_"):
            return

        # Извлекаем количество месяцев из payload
        parts = payload.split("_")
        months = int(parts[3])

        logger.info(f"Успешная оплата аренды сервера звездами: {months} мес., {payment_data.total_amount} звезд")

        # Рассчитываем даты
        start_date = datetime.datetime.now()
        end_date = start_date + datetime.timedelta(days=30 * months)

        # Добавляем запись в БД
        rent_id = add_server_rent(
            user_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            months=months,
            payment_amount=SERVER_RENT_PRICE * months,
            payment_method="stars",
            start_date=start_date,
            end_date=end_date
        )

        if rent_id > 0:
            await bot.send_message(
                chat_id=message.from_user.id,
                text=f"✅ <b>Аренда сервера успешно оплачена!</b>\n\n"
                     f"📅 Срок аренды: <b>{months} {'месяц' if months == 1 else 'месяца' if months < 5 else 'месяцев'}</b>\n"
                     f"📅 Дата начала: {start_date.strftime('%d.%m.%Y')}\n"
                     f"📅 Дата окончания: {end_date.strftime('%d.%m.%Y')}\n\n"
                     f"📡 Сервер теперь доступен для ваших задач!\n\n"
                     f"За подробностями обратитесь к @PyAdminRU",
                reply_markup=start_menu(),
                parse_mode="HTML"
            )

            # Уведомляем администратора
            await bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=f"⭐️ <b>Новая аренда сервера (Stars)!</b>\n\n"
                     f"👤 Пользователь:\n"
                     f"• ID: {message.from_user.id}\n"
                     f"• Username: @{message.from_user.username}\n"
                     f"• Имя: {message.from_user.first_name}\n\n"
                     f"📅 Срок: {months} мес.\n"
                     f"💰 Сумма: {payment_data.total_amount} ⭐️ ({SERVER_RENT_PRICE * months} ₽)\n"
                     f"📅 Окончание: {end_date.strftime('%d.%m.%Y')}\n"
                     f"🕒 Дата: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                parse_mode="HTML"
            )
        else:
            await message.answer("⚠️ Ошибка при сохранении аренды. Обратитесь к @PyAdminRU")

        await state.clear()

    except Exception as e:
        logger.exception(f"Ошибка при обработке оплаты аренды сервера: {e}")
        await message.answer("⚠️ Произошла ошибка при обработке платежа. Обратитесь к @PyAdminRU")
