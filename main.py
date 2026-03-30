import asyncio
import logging
import os  # Добавили для работы с системными переменными
from aiohttp import web # Добавили веб-сервер
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

# --- Секция Веб-сервера для Render ---
async def handle(request):
    return web.Response(text="Bot is running!")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    # Render передает порт в переменную PORT. Если её нет, используем 10000
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"Web server started on port {port}")

# --- Обработчики бота ---

# 1. Получение Business ID
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

# 2. Обработчик рассылки
@dp.message(F.photo)
async def start_broadcast(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

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
            await bot.send_photo(
                chat_id=chat,
                photo=photo_id,
                caption=caption,
                business_connection_id=BUSINESS_ID
            )
            success += 1
            await asyncio.sleep(1) 
        except Exception as e:
            logging.error(f"Ошибка в чате {chat}: {e}")
            errors += 1

    await status_msg.edit_text(
        f"🏁 <b>Рассылка завершена!</b>\n\n"
        f"✅ Успешно: {success}\n"
        f"❌ Ошибок: {errors}"
    )

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Бот запущен. Пришлите фото с описанием для рассылки.")

# --- Главная функция запуска ---
async def main():
    # Запускаем веб-сервер
    await start_web_server()
    
    print("Бот запущен и готов к работе!")
    
    # Запускаем поллинг (бот начинает слушать сообщения)
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Бот остановлен")
