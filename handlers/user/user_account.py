# -*- coding: utf-8 -*-
from aiogram import F, Router, types

from db.settings_db import UserPayment
from keyboards.user_keyboards import user_account_keyboard, start_menu
from system.dispatcher import bot, dp

router = Router(name=__name__)

@dp.callback_query(F.data == "user_account")
async def user_account_handlers(callback_query: types.CallbackQuery):
    """Кабинет пользователя"""

    message_text = (
        f"👋 Привет, <b>{callback_query.from_user.first_name}</b>!\n\n"
        "🔐 Ты вошёл в свой персональный кабинет — закрытую зону доступа, "
        "доступную только тебе.\n\n"
        "📦 Здесь ты можешь:\n"
        "   • Посмотреть свои покупки\n"
        "   • Управлять подписками\n"
        "   • Получить помощь и поддержку\n\n"
        "Спасибо, что пользуешься моими сервисами! 🙌"
    )

    await bot.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        text=message_text,
        reply_markup=user_account_keyboard(),
        disable_web_page_preview=True,
        parse_mode='HTML'
    )


def get_user_payments(user_id: int):
    """Все платежи пользователя, от новых к старым"""
    return list(
        UserPayment
        .select()
        .where(UserPayment.user_id == user_id)
        .order_by(UserPayment.date.desc())
    )


def get_user_payments_formatted(user_id: int) -> str:
    """
    Возвращает готовый текст для сообщения с заказами
    """
    payments = get_user_payments(user_id)

    if not payments:
        return "У вас пока нет оплаченных заказов."

    lines = ["📦 <b>Ваши заказы:</b>\n"]

    for i, p in enumerate(payments, 1):
        status_emoji = {
            'success': '✅',
            'paid': '✅',
            'complete': '✅',
            'failed': '❌',
            'pending': '⏳',
        }.get(p.payment_status.lower(), '⚪')

        date_str = p.date if p.date else "—"
        username_str = f"@{p.username}" if p.username else ""

        line = (
            f"{i}. {status_emoji} <b>{p.product}</b>\n"
            f"   Дата: {date_str}\n"
            f"   Статус: {p.payment_status}\n"
        )
        if p.first_name or username_str:
            line += f"   Покупатель: {p.first_name or ''} {username_str}\n"

        lines.append(line + "\n")

    return "\n".join(lines)


def user_has_product(user_id: int, product_name: str) -> bool:
    """Проверяет, есть ли успешная покупка конкретного продукта"""
    return UserPayment.select().where(
        (UserPayment.user_id == user_id) &
        (UserPayment.product == product_name) &
        (UserPayment.payment_status.in_(['success', 'paid', 'complete']))
    ).exists()


@router.callback_query(F.data == "my_orders")
async def my_orders_handlers(callback: types.CallbackQuery):
    """Покупки пользователя"""

    user_id = callback.from_user.id
    name = callback.from_user.first_name

    text = get_user_payments_formatted(user_id)

    full_text = (
        f"👋 <b>{name}</b>!\n\n"
        f"{text}"
    )

    try:
        await callback.message.edit_text(
            text=full_text,
            parse_mode="HTML",
            disable_web_page_preview=True,
            reply_markup=start_menu()
        )
    except Exception as e:
        await callback.message.edit_text(
            "Заказов слишком много для отображения в одном сообщении.\n"
            "Обратитесь в поддержку для детальной выписки.",
            reply_markup=start_menu()
        )

    await callback.answer()



