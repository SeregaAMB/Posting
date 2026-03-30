import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

# ================= НАСТРОЙКИ =================
API_TOKEN = '8654591106:AAGgcpDGJhp5uv2TvqTIVfU-J0NmSy7EOQo'  # Получите у @BotFather
ADMIN_ID = 8451820418          # Ваш числовой ID (узнать можно у @userinfobot)

# Сюда вставьте ID, который пришлет бот после подключения к бизнесу
BUSINESS_ID = 'ПОКА_ПУСТО' 

# Список чатов для рассылки (ID или @юзернеймы)
TARGET_CHATS = [
    '@chat_one', 
    -1001234567890
]
# ==============================================

logging.basicConfig(level=logging.INFO)

bot = Bot(
    token=API_TOKEN, 
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# 1. Получение Business ID (пришлет вам в личку)
@dp.business_connection()
async def handle_business_connection(connection: types.BusinessConnection):
    if connection.is_enabled:
        text = (
            f"✅ <b>Бот успешно подключен к бизнесу!</b>\n\n"
            f"Ваш BUSINESS_ID:\n<code>{connection.id}</code>\n\n"
            f"Скопируйте его, вставьте в код в переменную BUSINESS_ID и перезапустите бота на Render."
        )
        await bot.send_message(ADMIN_ID, text)
        print(f"ПОЛУЧЕН BUSINESS_ID: {connection.id}")

# 2. Обработчик рассылки (когда вы присылаете фото с текстом)
@dp.message(F.photo)
async def start_broadcast(message: types.Message):
    # Проверка, что пишет админ
    if message.from_user.id != ADMIN_ID:
        return

    # Проверка, настроен ли Business ID
    if BUSINESS_ID == 'ПОКА_ПУСТО':
        await message.answer("❌ Ошибка: В коде не указан <b>BUSINESS_ID</b>. Подключите бота в настройках Telegram Business и обновите код.")
        return

    photo_id = message.photo[-1].file_id
    caption = message.caption or ""
    
    status_msg = await message.answer("⏳ Начинаю рассылку от вашего имени...")
    
    success = 0
    errors = 0

    for chat in TARGET_CHATS:
        try:
            # Магия: отправка сообщения ОТ ВАШЕГО ЛИЦА
            await bot.send_photo(
                chat_id=chat,
                photo=photo_id,
                caption=caption,
                business_connection_id=BUSINESS_ID
            )
            success += 1
            await asyncio.sleep(1) # Задержка, чтобы Telegram не забанил
        except Exception as e:
            logging.error(f"Ошибка в чате {chat}: {e}")
            errors += 1

    await status_msg.edit_text(
        f"🏁 <b>Рассылка завершена!</b>\n\n"
        f"✅ Успешно: {success}\n"
        f"❌ Ошибок: {errors}"
    )

# Команда старт для проверки
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Бот запущен. Пришлите фото с описанием для рассылки.")

async def main():
    print("Бот запущен и готов к работе!")
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
