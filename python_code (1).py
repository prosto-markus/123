import asyncio
import json
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command

TOKEN = "8905219706:AAEhUewTdjcom8ofzKraGs8F-jTX4_HZ9Sw"
ADMIN_ID = 1737246390

bot = Bot(token=TOKEN)
dp = Dispatcher()

DATA_FILE = "pidor_list.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"pencil": [], "forever": []}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

@dp.message(F.reply_to_message & (F.text.strip().lower() == "!тетрадка"))
async def add_to_list(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    target_user = message.reply_to_message.from_user
    username = f"@{target_user.username}" if target_user.username else target_user.full_name
    data = load_data()
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

@dp.message(Command("тетрадка", prefix="!"))
async def show_list(message: types.Message):
    data = load_data()
    pencil_str = ", ".join(data["pencil"]) if data["pencil"] else "Пусто"
    forever_str = ", ".join(data["forever"]) if data["forever"] else "Пусто"
    text = f" **Список пидорасов, которых я ненавижу:**\n\n✏️ **Карандашиком:**\n{pencil_str}\n\n🔒 **Навсегда:**\n{forever_str}"
    await message.reply(text, parse_mode="Markdown")

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
        await message.reply(f"Стерто. {target_username} удален из тетрадки карандашиком.")
    elif target_username in data["forever"]:
        await message.reply("Этого уже не стереть, он в тетрадке навсегда. 🗿")
    else:
        await message.reply("Этого пользователя нет в тетрадке карандашиком.")

async def main():
    print("Бот фурыжит...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
