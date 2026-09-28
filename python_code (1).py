import asyncio
import json
import os
import re
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiohttp import web

TOKEN = "8905219706:AAEhUewTdjcom8ofzKraGs8F-jTX4_HZ9Sw" 
ADMIN_ID = 1737246390 

bot = Bot(token=TOKEN)
dp = Dispatcher()
DATA_FILE = "pidor_list.json"

# Безопасная загрузка базы данных
def load_data():
    if not os.path.exists(DATA_FILE) or os.path.getsize(DATA_FILE) == 0:
        return {"pencil": [], "forever": [], "elite": []}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, dict): data = {}
            if "pencil" not in data or not isinstance(data["pencil"], list): data["pencil"] = []
            if "forever" not in data or not isinstance(data["forever"], list): data["forever"] = []
            if "elite" not in data or not isinstance(data["elite"], list): data["elite"] = []
            return data
    except Exception:
        # Если файл поврежден, возвращаем чистую структуру, чтобы бот не падал
        return {"pencil": [], "forever": [], "elite": []}

# Безопасное сохранение базы данных (с принудительной кодировкой UTF-8)
def save_data(data):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Ошибка сохранения базы: {e}")

# Проверка прав администратора
def is_admin(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        return True
    if message.sender_chat and message.sender_chat.id:
        return True
    return False

# Настоящее имя автора из комментариев
def get_comment_author_name(reply_message: types.Message) -> str:
    if reply_message.author_signature:
        return str(reply_message.author_signature)
    if reply_message.sender_chat and reply_message.sender_chat.title:
        return str(reply_message.sender_chat.title)
    if reply_message.from_user:
        user = reply_message.from_user
        if user.username:
            return f"@{user.username}"
        return str(user.full_name)
    return "Неизвестный нарушитель"


# ==================== КОМАНДЫ ВЫВОДА СПИСКОВ (ПРОСТО ТЕКСТОМ) ====================

# 1. ВЫВОД СПИСКА ЭЛИТЫ (По команде !ангелы)
@dp.message(F.text)
async def commands_handler(message: types.Message):
    text = message.text.strip().lower()

    if text == "!ангелы":
        data = load_data()
        elite_str = ", ".join(data["elite"]) if data["elite"] else "Пусто"

        await message.reply(
            f"👑 Список неприкасаемой элиты чата:\n\n{elite_str}"
        )

    elif text == "!список":
        data = load_data()

        pencil_str = ", ".join(data["pencil"]) if data["pencil"] else "Пусто"
        forever_str = ", ".join(data["forever"]) if data["forever"] else "Пусто"

        await message.reply(
            f"📖 Список пидорасов:\n\n"
            f"✏️ Карандашиком:\n{pencil_str}\n\n"
            f"🔒 Навсегда:\n{forever_str}"
        )

# ==================== КОМАНДЫ УПРАВЛЕНИЯ (СТРОГО ЧЕРЕЗ РЕПЛАЙ) ====================

# 3. ДОБАВЛЕНИЕ В ЭЛИТУ (Через реплай словом !элита)
@dp.message(F.reply_to_message & F.text.lower().contains("!элита"))
async def add_to_elite(message: types.Message):
    if not is_admin(message):
        return
        
    username = get_comment_author_name(message.reply_to_message)
    if username in ["Telegram", "Неизвестный нарушитель"] and message.reply_to_message.from_user:
        username = str(message.reply_to_message.from_user.full_name)
        
    data = load_data()
    if username in data["elite"]:
        await message.reply(f"{username} уже находится в списке элиты. ✨")
        return
        
    if username in data["pencil"]: data["pencil"].remove(username)
    if username in data["forever"]: data["forever"].remove(username)
        
    data["elite"].append(username)
    save_data(data)
    await message.reply(f"{username} добавлен в список элиты! 👑 Его больше нельзя занести в тетрадку.")

# 4. ДОБАВЛЕНИЕ В ТЕТРАДКУ (По словам !тетрадка или !пидор через реплай)
@dp.message(F.reply_to_message & (F.text.lower().contains("!тетрадка") | F.text.lower().contains("!пидор")))
async def add_to_list(message: types.Message):
    if not is_admin(message):
        return
        
    username = get_comment_author_name(message.reply_to_message)
    if username in ["Telegram", "Неизвестный нарушитель"] and message.reply_to_message.from_user:
        username = str(message.reply_to_message.from_user.full_name)

    data = load_data()
    if username in data["elite"]:
        await message.reply(f"Этого пользователя нельзя добавить в тетрадку, он в списке элиты! 👑")
        return
    if username in data["forever"]:
        await message.reply(f"{username} уже в тетрадке пидерасов навсегда. Тут без шансов.")
        return
        
    if username in data["pencil"]:
        data["pencil"].remove(username)
        data["forever"].append(username)
        save_data(data)
        await message.reply(f"{username} в тетрадке пидорасов навсегда. ⛔")
    else:
        data["pencil"].append(username)
        save_data(data)
        await message.reply(f"{username} в тетрадке пидорасов, но пока карандашиком. ✏️")

# 5. ОЧИСТКА КАРАНДАШИКА (Через реплай словом !удалить)
@dp.message(F.reply_to_message & F.text.lower().contains("!удалить"))
async def remove_from_pencil(message: types.Message):
    if not is_admin(message):
        return
        
    username = get_comment_author_name(message.reply_to_message)
    if username in ["Telegram", "Неизвестный нарушитель"] and message.reply_to_message.from_user:
        username = str(message.reply_to_message.from_user.full_name)
        
    data = load_data()
    if username in data["pencil"]:
        data["pencil"].remove(username)
        save_data(data)
        await message.reply(f"Стерто. {username} удален из тетрадки карандашиком. 🧽")
    elif username in data["forever"]:
        await message.reply("Этого уже не стереть, он в тетрадке навсегда. 🗿")
    else:
        await message.reply("Этого пользователя нет в тетрадке карандашиком.")

async def handle(request):
    return web.Response(text="Bot is running!")

async def main():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.environ.get("PORT", 10000)))
    await site.start()
    
    print("Бот фурыжит...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
