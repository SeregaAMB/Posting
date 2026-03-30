import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command

# --- НАСТРОЙКИ ---
API_TOKEN = '8654591106:AAGgcpDGJhp5uv2TvqTIVfU-J0NmSy7EOQo'
ADMIN_ID = 8451820418  # Ваш личный ID (цифрами)

# Сюда вы вставите ID, который бот напишет вам в консоли после запуска
BUSINESS_ID = 'ПОКА_ПУСТО' 

# Список чатов (ID или юзернеймы)
TARGET_CHATS = [
    '@chat_username1', 
    -100123456789
]

# Настройка логирования
logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- 1. ФУНКЦИЯ ДЛЯ ПОЛУЧЕНИЯ BUSINESS_ID ---
# Как только вы подключите бота в меню "Telegram для бизнеса", 
# этот код выведет ваш ID в консоль (терминал).
@dp.business_connection()
async def handle_business_connection(connection: types.BusinessConnection):
    print("\n" + "="*50)
    print(f"🔥 ВАШ BUSINESS_ID: {connection.id}")
    print("Скопируйте его и вставьте в переменную BUSINESS_ID в начале кода!")
    print("="*50 + "\n")

# --- 2. ОБРАБОТЧИК РАССЫЛКИ ---
@dp.message(F.photo)
async def handle_admin_photo_post(message: types.Message):
    # Проверка прав
    if message.from_user.id != ADMIN_ID:
        return

    # Проверка, заполнен ли ID
    if BUSINESS_ID == 'ПОКА_ПУСТО':
        await message.answer("⚠️ Вы не указали BUSINESS_ID в коде! Посмотрите в консоль бота, там должен быть ваш ID.")
        return

    photo_id = message.photo[-1].file_id
    caption = message.caption or ""

    confirm_msg = await message.answer("🚀 Начинаю рассылку от вашего имени...")
    
    success_count = 0
    error_count = 0

    for chat_id in TARGET_CHATS:
        try:
            # Отправка через бизнес-аккаунт
            await bot.send_photo(
                chat_id=chat_id,
                photo=photo_id,
                caption=caption,
                business_connection_id=BUSINESS_ID
            )
            success_count += 1
            await asyncio.sleep(2) # Защита от спам-фильтра
        except Exception as e:
            logging.error(f"Ошибка в {chat_id}: {e}")
            error_count += 1

    await confirm_msg.edit_text(
        f"✅ Рассылка завершена!\n\n"
        f"Успешно: {success_count}\n"
        f"Ошибок: {error_count}"
    )

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer("Бот готов. Пришли фото с текстом для рассылки.")

async def main():
    print("Бот запущен. Ожидаю бизнес-соединение...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот выключен")
