import asyncio
import json
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiohttp import web

TOKEN = "8905219706:AAEhUewTdjcom8ofzKraGs8F-jTX4_HZ9Sw" 
ADMIN_ID = 1737246390 

bot = Bot(token=TOKEN)
dp = Dispatcher()
DATA_FILE = "pidor_list.json"

# Загрузка и сохранение базы данных
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except Exception:
                data = {}
            # Гарантируем, что внутри всегда будут чистые списки строк
            if "pencil" not in data or not isinstance(data["pencil"], list): data["pencil"] = []
            if "forever" not in data or not isinstance(data["forever"], list): data["forever"] = []
            if "elite" not in data or not isinstance(data["elite"], list): data["elite"] = []
            return data
    return {"pencil": [], "forever": [], "elite": []}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Проверка прав администратора (Вы лично или от имени Канала)
def is_admin(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        return True
    if message.sender_chat and message.sender_chat.id:
        return True
    return False

# Функция для вытаскивания красивого имени пользователя СТРОГО как строки (str)
def get_user_display_name(user: types.User) -> str:
    if user.username:
        return f"@{user.username}"
    return str(user.full_name)

# 1. Внесение в ТЕТРАДКУ (ЧЕРЕЗ ОТВЕТ НА СООБЩЕНИЕ НАРУШИТЕЛЯ)
@dp.message(F.reply_to_message & (F.text.strip().lower() == "!тетрадка"))
async def add_to_list(message: types.Message):
    if not is_admin(message):
        return
        
    target_user = message.reply_to_message.from_user
    if not target_user and message.reply_to_message.sender_chat:
        username = str(message.reply_to_message.sender_chat.title)
    elif target_user:
        username = get_user_display_name(target_user)
    else:
        await message.reply("Не удалось определить пользователя для добавления.")
        return

    data = load_data()
    
    if username in data["elite"]:
        await message.reply(f"Этого пользователя нельзя добавить в тетрадку, он в списке элиты! 👑")
        return

    if username in data["forever"]:
        await message.reply(f"{username} уже в тетрадке пидорасов навсегда. Тут без шансов.")
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

# 2. Добавление в список ЭЛИТЫ (ЧЕРЕЗ ОТВЕТ НА СООБЩЕНИЕ КОМАНДОЙ !элита)
@dp.message(F.reply_to_message & (F.text.strip().lower() == "!элита"))
async def add_to_elite(message: types.Message):
    if not is_admin(message):
        return
        
    target_user = message.reply_to_message.from_user
    if not target_user and message.reply_to_message.sender_chat:
        username = str(message.reply_to_message.sender_chat.title)
    elif target_user:
        username = get_user_display_name(target_user)
    else:
        return
        
    data = load_data()
    if username in data["elite"]:
        await message.reply(f"{username} уже находится в списке элиты. ✨")
        return
        
    if username in data["pencil"]:
        data["pencil"].remove(username)
    if username in data["forever"]:
        data["forever"].remove(username)
        
    data["elite"].append(username)
    save_data(data)
    await message.reply(f"{username} добавлен в список элиты! 👑 Его больше нельзя занести в тетрадку.")

# 3. Вывод списков по обычным командам (Просто пишем в чат БЕЗ ОТВЕТОВ)
@dp.message(Command("тетрадка", prefix="!"))
async def show_list(message: types.Message):
    data = load_data()
    
    # Фильтруем базу на случай, если там остались старые поломанные массивы
    clean_pencil = [str(x) for x in data["pencil"] if isinstance(x, str)]
    clean_forever = [str(x) for x in data["forever"] if isinstance(x, str)]
    
    pencil_str = ", ".join(clean_pencil) if clean_pencil else "Пусто"
    forever_str = ", ".join(clean_forever) if clean_forever else "Пусто"
    
    text = (
        "**Список пидорасов, которых я ненавижу:**\n\n"
        f"✏️ **Карандашиком:**\n{pencil_str}\n\n"
        f"🔒 **Навсегда:**\n{forever_str}"
    )
    await message.reply(text, parse_mode="Markdown")

@dp.message(Command("список_элиты", prefix="!"))
async def show_elite_list(message: types.Message):
    data = load_data()
    clean_elite = [str(x) for x in data["elite"] if isinstance(x, str)]
    elite_str = ", ".join(clean_elite) if clean_elite else "Пусто"
    text = f"👑 **Список неприкасаемой элиты чата:**\n\n{elite_str}"
    await message.reply(text, parse_mode="Markdown")

# 4. Очистка списка карандашиком (ЧЕРЕЗ ОТВЕТ НА СООБЩЕНИЕ КОМАНДОЙ !удалить)
@dp.message(F.reply_to_message & (F.text.strip().lower() == "!удалить"))
async def remove_from_pencil(message: types.Message):
    if not is_admin(message):
        return
        
    target_user = message.reply_to_message.from_user
    if not target_user and message.reply_to_message.sender_chat:
        username = str(message.reply_to_message.sender_chat.title)
    elif target_user:
        username = get_user_display_name(target_user)
    else:
        return
        
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
