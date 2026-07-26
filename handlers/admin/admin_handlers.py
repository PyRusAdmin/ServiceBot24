import datetime

from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from loguru import logger

from db.settings_db import get_all_users, is_user_in_db, add_user_to_db, set_product_password, set_maxmaster_password
from states.states import AdminState
from system.dispatcher import bot, ADMIN_CHAT_ID

router = Router(name=__name__)


@router.message(Command('admin_help'))
async def admin_help_handler(message: types.Message):
    """
    Справка по админским командам
    """
    # Проверяем, является ли пользователь администратором
    if str(message.from_user.id) != str(ADMIN_CHAT_ID):
        await message.answer("❌ У вас нет доступа к админским командам.")
        return

    help_text = """
🔧 <b>Админские команды бота</b> 🔧

📋 <b>Доступные команды:</b>

1️⃣ <b>/admin_help</b> - Показать эту справку

2️⃣ <b>/broadcast</b> - Начать рассылку сообщения всем пользователям

3️⃣ <b>/stats</b> - Показать статистику пользователей бота

4️⃣ <b>/pass</b> - Установить пароль для TelegramMaster-PRO

5️⃣ <b>/id</b> - Добавить пользователя в базу данных по ID

6️⃣ <b>/maxmaster_pass</b> - Установить пароль для MaxMaster

📝 <b>Как использовать рассылку:</b>

Шаг 1. Отправьте команду /broadcast

Шаг 2. Бот попросит вас ввести текст сообщения для рассылки

Шаг 3. Введите текст сообщения (можно использовать HTML-разметку)

Шаг 4. Бот покажет статистику: сколько всего пользователей и сколько сообщений отправлено

⚠️ <b>Важно:</b>
• Рассылка отправляется всем пользователям, которые хотя бы раз запускали бота
• Используйте разметку осторожно (HTML)
• Большие рассылки могут занять некоторое время

🔐 <b>Как установить пароль:</b>
<code>/pass</code> → <code>Введите новый пароль</code> → Пароль сохранен

📊 <b>Пример использования:</b>
<code>/broadcast</code> → <code>Уважаемые пользователи! У нас обновился функционал...</code>
"""

    await message.answer(help_text, parse_mode="HTML")


@router.message(Command('broadcast'))
async def start_broadcast_handler(message: types.Message, state: FSMContext):
    """
    Начало рассылки сообщений пользователям
    """
    # Проверяем, является ли пользователь администратором
    if str(message.from_user.id) != str(ADMIN_CHAT_ID):
        await message.answer("❌ У вас нет доступа к этой команде.")
        return

    await message.answer(
        "📨 <b>Рассылка сообщений</b>\n\n"
        "Введите текст сообщения, которое вы хотите отправить всем пользователям:\n\n"
        "⚠️ Можно использовать HTML-разметку",
        parse_mode="HTML"
    )
    await state.set_state(AdminState.waiting_for_broadcast_message)


@router.message(AdminState.waiting_for_broadcast_message)
async def process_broadcast_message(message: types.Message, state: FSMContext):
    """
    Обработка сообщения для рассылки и отправка пользователям
    """
    # Проверяем, является ли пользователь администратором
    if str(message.from_user.id) != str(ADMIN_CHAT_ID):
        await message.answer("❌ У вас нет доступа к этой команде.")
        await state.clear()
        return

    broadcast_text = message.text
    logger.info(f"Администратор {message.from_user.id} начал рассылку")

    # Получаем всех пользователей из базы данных
    users = get_all_users()

    if not users:
        await message.answer("❌ В базе данных нет пользователей для рассылки.")
        await state.clear()
        return

    total_users = len(users)
    success_count = 0
    error_count = 0

    # Отправляем сообщение всем пользователям
    for user in users:
        try:
            await bot.send_message(
                chat_id=user['user_id'],
                text=broadcast_text,
                parse_mode="HTML"
            )
            success_count += 1
        except Exception as e:
            logger.error(f"Не удалось отправить сообщение пользователю {user['user_id']}: {e}")
            error_count += 1

    # Отправляем отчет администратору
    report = (
        f"✅ <b>Рассылка завершена</b>\n\n"
        f"📊 <b>Статистика:</b>\n"
        f"• Всего пользователей: {total_users}\n"
        f"• Успешно отправлено: {success_count}\n"
        f"• Ошибок: {error_count}\n\n"
        f"🕒 Время завершения: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

    await message.answer(report, parse_mode="HTML")
    logger.info(f"Рассылка завершена. Успешно: {success_count}, Ошибок: {error_count}")
    await state.clear()


@router.message(Command('stats'))
async def stats_handler(message: types.Message):
    """
    Показывает статистику пользователей бота
    """
    # Проверяем, является ли пользователь администратором
    if str(message.from_user.id) != str(ADMIN_CHAT_ID):
        await message.answer("❌ У вас нет доступа к этой команде.")
        return

    users = get_all_users()
    total_users = len(users) if users else 0

    stats_text = (
        f"📊 <b>Статистика бота</b> 📊\n\n"
        f"👥 Всего пользователей: {total_users}\n\n"
        f"🕒 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

    await message.answer(stats_text, parse_mode="HTML")


# ============================================================================
# Админские команды для управления паролем
# ============================================================================

@router.message(Command('pass'))
async def send_pass(message: types.Message, state: FSMContext):
    """
    Обработчик команды /pass для установки пароля в бота
    Доступно только администратору
    """
    # Проверяем, является ли пользователь администратором
    if str(message.from_user.id) != str(ADMIN_CHAT_ID):
        await message.answer("❌ У вас нет доступа к этой команде.")
        return

    await message.answer(
        '🔐 <b>Установка пароля для TelegramMaster-PRO</b>\n\n'
        'Введите новый пароль:',
        parse_mode="HTML"
    )
    await state.set_state(AdminState.waiting_for_password)


@router.message(AdminState.waiting_for_password)
async def save_password(message: types.Message, state: FSMContext):
    """
    Обработчик состояния waiting_for_password
    Сохраняет пароль в базу данных
    """
    # Проверяем, является ли пользователь администратором
    if str(message.from_user.id) != str(ADMIN_CHAT_ID):
        await message.answer("❌ У вас нет доступа к этой команде.")
        await state.clear()
        return

    password = message.text  # Получаем текст сообщения

    try:
        # Сохраняем пароль в базу данных
        result = set_product_password("TelegramMaster-PRO", password)

        if result:
            logger.info(f"Администратор {message.from_user.id} обновил пароль для TelegramMaster-PRO")
            await message.answer(
                f"✅ <b>Пароль успешно сохранен!</b>\n\n"
                f"Пароль: <code>{password}</code>",
                parse_mode="HTML"
            )
        else:
            await message.answer("❌ Ошибка при сохранении пароля. Попробуйте позже.")
    except Exception as e:
        logger.exception(f"Ошибка при сохранении пароля: {e}")
        await message.answer("❌ Ошибка при сохранении пароля. Проверьте логи.")

    await state.clear()


# ============================================================================
# Админские команды для работы с пользователями
# ============================================================================

@router.message(Command('id'))
async def process_id_command(message: types.Message):
    """
    Обработчик команды /id для добавления пользователя в базу данных
    Доступно только администратору
    Использование: /id <user_id>
    """
    # Проверяем, является ли пользователь администратором
    if str(message.from_user.id) != str(ADMIN_CHAT_ID):
        await message.answer("❌ У вас нет доступа к этой команде.")
        return

    try:
        user_id = int(message.text.split()[1])
        result = is_user_in_db(user_id)  # Проверка наличия ID в базе данных

        if result is None:
            add_user_to_db(user_id)
            await message.reply(f"✅ ID {user_id} успешно записан в базу данных.")
            logger.info(f"Администратор {message.from_user.id} добавил пользователя {user_id} в базу данных")
        else:
            await message.reply(f"⚠️ ID {user_id} уже существует в базе данных.")
    except (IndexError, ValueError):
        await message.reply(
            "❌ Неверный формат команды.\n\n"
            "Используйте: <code>/id &lt;user_id&gt;</code>\n"
            "Пример: <code>/id 123456789</code>",
            parse_mode="HTML"
        )
    except Exception as error:
        logger.exception(f"Ошибка при обработке команды /id: {error}")
        await message.reply("❌ Произошла ошибка при выполнении команды.")


# ============================================================================
# Админские команды для MaxMaster
# ============================================================================

@router.message(Command('maxmaster_pass'))
async def send_maxmaster_pass(message: types.Message, state: FSMContext):
    """
    Обработчик команды /maxmaster_pass для установки пароля MaxMaster
    Доступно только администратору
    """
    # Проверяем, является ли пользователь администратором
    if str(message.from_user.id) != str(ADMIN_CHAT_ID):
        await message.answer("❌ У вас нет доступа к этой команде.")
        return

    await message.answer(
        '🔐 <b>Установка пароля для MaxMaster</b>\n\n'
        'Введите пароль от архива MaxMaster:',
        parse_mode="HTML"
    )
    await state.set_state(AdminState.waiting_for_maxmaster_password)


@router.message(AdminState.waiting_for_maxmaster_password)
async def save_maxmaster_password(message: types.Message, state: FSMContext):
    """
    Обработчик состояния waiting_for_maxmaster_password
    Сохраняет пароль MaxMaster в базу данных
    """
    # Проверяем, является ли пользователь администратором
    if str(message.from_user.id) != str(ADMIN_CHAT_ID):
        await message.answer("❌ У вас нет доступа к этой команде.")
        await state.clear()
        return

    password = message.text  # Получаем текст сообщения

    try:
        # Сохраняем пароль в базу данных
        result = set_maxmaster_password(password)

        if result:
            logger.info(f"Администратор {message.from_user.id} обновил пароль для MaxMaster")
            await message.answer(
                f"✅ <b>Пароль MaxMaster успешно сохранен!</b>\n\n"
                f"Пароль: <code>{password}</code>",
                parse_mode="HTML"
            )
        else:
            await message.answer("❌ Ошибка при сохранении пароля. Попробуйте позже.")
    except Exception as e:
        logger.exception(f"Ошибка при сохранении пароля MaxMaster: {e}")
        await message.answer("❌ Ошибка при сохранении пароля. Проверьте логи.")

    await state.clear()
