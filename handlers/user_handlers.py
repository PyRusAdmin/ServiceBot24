from aiogram import types
from aiogram.dispatcher import FSMContext  # Состояния пользователя

from keyboards.user_keyboards import greeting_keyboards  # Клавиатуры поста приветствия
from messages.user_messages import greeting_post  # Пояснение для пользователя FAG
from system.dispatcher import dp, bot, CHANNEL_ID  # Подключение к боту и диспетчеру пользователя


@dp.message_handler(commands=['start'])
async def greeting(message: types.Message, state: FSMContext):
    """Обработчик команды /start, он же пост приветствия"""
    await state.finish()
    await state.reset_state()
    keyboards_greeting = greeting_keyboards()
    # Клавиатура для Калькулятора цен или Контактов
    await message.reply(greeting_post, reply_markup=keyboards_greeting, disable_web_page_preview=True,
                        parse_mode=types.ParseMode.HTML)


@dp.callback_query_handler(text='get_password')
async def get_password(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id

    # Проверка подписки на канал
    user = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
    if user.status == "member" or user.status == "administrator":
        # Пользователь подписан, отправляем файл с паролем
        # Замените 'password.txt' на путь к файлу с паролем
        with open('setting/password.txt', 'rb') as password_file:
            await bot.send_document(chat_id, password_file)
    else:
        # Пользователь не подписан, отправляем сообщение с просьбой подписаться
        await bot.send_message(chat_id, "Пожалуйста, подпишитесь на канал @TG_SMM2 и попробуйте снова.")


def greeting_handler():
    """Регистрируем handlers для бота"""
    dp.register_message_handler(greeting)  # Обработчик команды /start, он же пост приветствия
