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

# Функция проверки прав (Слушается вас лично ИЛИ вас, когда вы пишете от имени Канала/Группы)
def is_admin(message: types.Message):
    # 1. Проверка по вашему личному ID
    if message.from_user.id == ADMIN_ID:
        return True
    # 2. Проверка, если сообщение отправлено от имени канала или анонимного создателя чата
    if message.sender_chat and message.sender_chat.id:
        return True
    return False

# 1. Управление ТЕТРАДКОЙ (Добавление по нику ИЛИ просмотр статистики для ВСЕХ)
@dp.message(F.text.strip().lower().startswith("!тетрадка"))
async def handle_notebook(message: types.Message):
    args = message.text.split()
    data = load_data()
    
    # ЕСЛИ НАПИСАНО ПРОСТО "!тетрадка" — выводим список для ВСЕХ
    if len(args) == 1:
        pencil_str = ", ".join(data["pencil"]) if data["pencil"] else "Пусто"
        forever_str = ", ".join(data["forever"]) if data["forever"] else "Пусто"
        text = f"**Список пидорасов, которых я ненавижу:**\n\n✏️ **Карандашиком:**\n{pencil_str}\n\n🔒 **Навсегда:**\n{forever_str}"
        await message.reply(text, parse_mode="Markdown")
        return
        
    # ЕСЛИ НАПИСАНО "!тетрадка @username" — проверяем права админа
    if not is_admin(message):
        return

    username = args[1]
    if not username.startswith("@"):
        await message.reply("Укажите ник пользователя обязательно с собачкой. Пример: `!тетрадка @username`")
        return
        
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

# 2. Добавление в список ЭЛИТЫ (команда !элита @username)
@dp.message(F.text.strip().lower().startswith("!элита"))
async def handle_elite(message: types.Message):
    if not is_admin(message):
        return
        
    args = message.text.split()
    if len(args) < 2:
        await message.reply("Укажите ник. Пример: `!элита @username`")
        return
        
    username = args[1]
    if not username.startswith("@"):
        await message.reply("Укажите ник с собачкой. Пример: `!элита @username`")
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

# 3. Удаление из списка элиты (команда !убрать_элиту @username)
@dp.message(Command("убрать_элиту", prefix="!"))
async def remove_from_elite(message: types.Message):
    if not is_admin(message):
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

# 4. Вызов списка элиты (доступно для всех)
@dp.message(Command("список_элиты", prefix="!"))
async def show_elite_list(message: types.Message):
    data = load_data()
    elite_str = ", ".join(data["elite"]) if data["elite"] else "Пусто"
    text = f"👑 **Список неприкасаемой элиты чата:**\n\n{elite_str}"
    await message.reply(text, parse_mode="Markdown")

# 5. Редактирование (удаление из тетрадки «карандашиком»)
@dp.message(Command("удалить", prefix="!"))
async def remove_from_pencil(message: types.Message):
    if not is_admin(message):
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
