# -*- coding: utf-8 -*-
"""
Обработчики оплаты для аренды сервера
"""
import datetime

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from loguru import logger
from yookassa import Payment

from db.settings_db import add_server_rent, get_active_server_rent
from handlers.payment_yookassa import payment_yookassa_com
from handlers.payments.products_goods_services import SERVER_RENT_PRICE
from keyboards.user_keyboards import start_menu
from system.dispatcher import bot, ADMIN_CHAT_ID

router = Router(name=__name__)

product = "Аренда сервера"





@router.callback_query(F.data == "payment_yookassa_server_rent")
async def server_rent_handler(callback_query: types.CallbackQuery, state: FSMContext):
    """Выбор количества месяцев для аренды сервера"""

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

    # Создаем клавиатуру с выбором месяцев
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="1 месяц - 250 ₽", callback_data="rent_1_month")],
        [InlineKeyboardButton(text="2 месяца - 500 ₽", callback_data="rent_2_months")],
        [InlineKeyboardButton(text="3 месяца - 750 ₽", callback_data="rent_3_months")],
        [InlineKeyboardButton(text="6 месяцев - 1500 ₽", callback_data="rent_6_months")],
        [InlineKeyboardButton(text="12 месяцев - 3000 ₽", callback_data="rent_12_months")],
        [InlineKeyboardButton(text="🏠 В главное меню", callback_data="start_menu_keyboard")],
    ])

    await bot.send_message(
        chat_id=callback_query.from_user.id,
        text="🖥️ <b>Аренда сервера</b>\n\n"
             "Выберите срок аренды сервера:\n\n"
             "💰 <b>Цена:</b> 250 ₽/месяц\n"
             "⚡️ <b>Скидки:</b>\n"
             "• 6 месяцев - 1500 ₽ (экономия 1500 ₽)\n"
             "• 12 месяцев - 3000 ₽ (экономия 3000 ₽)\n\n"
             "📡 Сервер будет доступен 24/7 для ваших задач",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback_query.answer()


@router.callback_query(F.data.startswith("rent_"))
async def select_months_handler(callback_query: types.CallbackQuery, state: FSMContext):
    """Обработчик выбора количества месяцев"""
    # Извлекаем количество месяцев из callback_data
    months = int(callback_query.data.split("_")[1])
    price = SERVER_RENT_PRICE * months

    # Сохраняем выбранные месяцы в состоянии
    await state.update_data(months=months, price=price)

    # Создаем платеж YooKassa
    try:
        payment_url, payment_id = payment_yookassa_com(
            description_text=f"Аренда сервера на {months} мес.",
            product_price=price
        )

        # Сохраняем payment_id в состоянии
        await state.update_data(payment_id=payment_id, months=months, price=price)
        await state.set_state(ServerRentState.waiting_for_payment)

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='✅ Проверить оплату', callback_data=f"check_server_rent_{payment_id}")],
            [InlineKeyboardButton(text='🏠 В главное меню', callback_data='start_menu_keyboard')],
        ])

        await bot.send_message(
            chat_id=callback_query.from_user.id,
            text=f"💳 <b>Оплата аренды сервера</b>\n\n"
                 f"📅 Срок: <b>{months} {'месяц' if months == 1 else 'месяца' if months < 5 else 'месяцев'}</b>\n"
                 f"💰 Сумма: <b>{price} ₽</b>\n\n"
                 f"🔗 <a href='{payment_url}'>Перейти к оплате</a>\n\n"
                 f"После оплаты нажмите кнопку 'Проверить оплату'",
            reply_markup=keyboard,
            parse_mode="HTML"
        )

    except Exception as e:
        logger.exception(f"Ошибка при создании платежа аренды сервера: {e}")
        await bot.send_message(
            chat_id=callback_query.from_user.id,
            text="⚠️ Произошла ошибка при создании платежа. Пожалуйста, попробуйте позже."
        )

    await callback_query.answer()


@router.callback_query(F.data.startswith("check_server_rent_"))
async def check_server_rent_payment(callback_query: types.CallbackQuery, state: FSMContext):
    """Проверка оплаты аренды сервера"""
    try:
        payment_id = callback_query.data.split("_")[3]
        payment_info = Payment.find_one(payment_id)

        if payment_info.status == "succeeded":
            # Получаем данные из состояния
            state_data = await state.get_data()
            months = state_data.get('months')

            if not months:
                # Если данных нет в состоянии, извлекаем из БД (резервный вариант)
                await bot.send_message(
                    chat_id=callback_query.from_user.id,
                    text="⚠️ Ошибка: не найдены данные о платеже. Обратитесь к @PyAdminRU"
                )
                await state.clear()
                return

            # Рассчитываем даты
            start_date = datetime.datetime.now()
            end_date = start_date + datetime.timedelta(days=30 * months)

            # Добавляем запись в БД
            rent_id = add_server_rent(
                user_id=callback_query.from_user.id,
                username=callback_query.from_user.username,
                first_name=callback_query.from_user.first_name,
                last_name=callback_query.from_user.last_name,
                months=months,
                payment_amount=SERVER_RENT_PRICE * months,
                payment_method="yookassa",
                start_date=start_date,
                end_date=end_date
            )

            if rent_id > 0:
                await bot.send_message(
                    chat_id=callback_query.from_user.id,
                    text=f"✅ <b>Аренда сервера успешно оплачена!</b>\n\n"
                         f"📅 Срок аренды: <b>{months} {'месяц' if months == 1 else 'месяца' if months < 5 else 'месяцев'}</b>\n"
                         f"📅 Дата начала: {start_date.strftime('%d.%m.%Y')}\n"
                         f"📅 Дата окончания: {end_date.strftime('%d.%m.%Y')}\n\n"
                         f"📡 Сервер теперь доступен для ваших задач!\n\n"
                         f"За подробностями обратитесь к @PyAdminRU",
                    reply_markup=start_menu(),
                    parse_mode="HTML"
                )

                # Уведомляем админа
                await bot.send_message(
                    chat_id=ADMIN_CHAT_ID,
                    text=f"🖥️ <b>Новая аренда сервера!</b>\n\n"
                         f"👤 Пользователь:\n"
                         f"• ID: {callback_query.from_user.id}\n"
                         f"• Username: @{callback_query.from_user.username}\n"
                         f"• Имя: {callback_query.from_user.first_name}\n\n"
                         f"📅 Срок: {months} мес.\n"
                         f"💰 Сумма: {SERVER_RENT_PRICE * months} ₽ (YooKassa)\n"
                         f"📅 Окончание: {end_date.strftime('%d.%m.%Y')}\n"
                         f"🕒 Дата: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                    parse_mode="HTML"
                )
            else:
                await bot.send_message(
                    chat_id=callback_query.from_user.id,
                    text="⚠️ Ошибка при сохранении аренды. Обратитесь к @PyAdminRU"
                )

            await state.clear()
        else:
            await bot.send_message(
                chat_id=callback_query.message.chat.id,
                text="❌ Платеж еще не оплачен. Пожалуйста, завершите оплату и нажмите кнопку 'Проверить оплату' еще раз."
            )
    except Exception as e:
        logger.exception(f"Ошибка при проверке оплаты аренды сервера: {e}")
        await bot.send_message(
            chat_id=callback_query.message.chat.id,
            text="⚠️ Произошла ошибка при проверке оплаты. Пожалуйста, попробуйте позже."
        )
