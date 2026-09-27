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
            data = json.load(f)
            if "elite" not in data:  
                data["elite"] = []
            return data
    return {"pencil": [], "forever": [], "elite": []}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# 1. Внесение в тетрадку (через ОТВЕТ на сообщение)
@dp.message(F.reply_to_message & (F.text.strip().lower() == "!тетрадка"))
async def add_to_list(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    
    target_user = message.reply_to_message.from_user
    username = f"@{target_user.username}" if target_user.username else target_user.full_name
    
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

# 2. Добавление в список ЭЛИТЫ (через ОТВЕТ на сообщение командой !элита)
@dp.message(F.reply_to_message & (F.text.strip().lower() == "!элита"))
async def add_to_elite(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
        
    target_user = message.reply_to_message.from_user
    username = f"@{target_user.username}" if target_user.username else target_user.full_name
    
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

# 3. Удаление из списка элиты (команда !убрать_элиту @username)
@dp.message(Command("убрать_элиту", prefix="!"))
async def remove_from_elite(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    args = message.text.split()
    if len(args) < 2:
        await message.reply("Укажите ник. Пример: `!убрать_элиту @username`")
        return
    target_username = args[1]
    data = load_data()
    if target_username in data["elite"]:
        data["elite"].remove(target_username)
        save_data(data)
        await message.reply(f"{target_username} лишен статуса элиты. Теперь он обычный смертный. 🧽")
    else:
        await message.reply("Этого пользователя нет в списке элиты.")

# 4. Вызов списка элиты (доступно ТОЛЬКО вам)
@dp.message(Command("список_элиты", prefix="!"))
async def show_elite_list(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    data = load_data()
    elite_str = ", ".join(data["elite"]) if data["elite"] else "Пусто"
    text = f"👑 **Список неприкасаемой элиты:**\n\n{elite_str}"
    await message.reply(text, parse_mode="Markdown")

# 5. Вывод действующей тетрадки (без элиты)
@dp.message(Command("тетрадка", prefix="!"))
async def show_list(message: types.Message):
    data = load_data()
    pencil_str = ", ".join(data["pencil"]) if data["pencil"] else "Пусто"
    forever_str = ", ".join(data["forever"]) if data["forever"] else "Пусто"
    text = f"**Список пидорасов, которых я ненавижу:**\n\n✏️ **Карандашиком:**\n{pencil_str}\n\n🔒 **Навсегда:**\n{forever_str}"
    await message.reply(text, parse_mode="Markdown")

# 6. Редактирование (удаление из тетрадки «карандашиком»)
@dp.message(Command("удалить", prefix="!"))
async def remove_from_pencil(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    args = message.text.split()
    if len(args) < 2:
        await message.reply("Укажите ник. Пример: `!удалить @username`")
        return
    target_username = args[1]
    data = load_data()
    if target_username in data["pencil"]:
        data["pencil"].remove(target_username)
        save_data(data)
        await message.reply(f"Стерто. {target_username} удален из тетрадки карандашиком. 🧽")
    elif target_username in data["forever"]:
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
