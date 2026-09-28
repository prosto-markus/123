import asyncio
import json
import os
from aiogram import Bot, Dispatcher, types, F
from aiohttp import web

# Токен берем из переменных окружения (безопасно)
TOKEN = os.environ.get("BOT_TOKEN", "8905219706:AAEhUewTdjcom8ofzKraGs8F-jTX4_HZ9Sw")
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
        return {"pencil": [], "forever": [], "elite": []}

# Безопасное сохранение базы данных
def save_data(data):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Ошибка сохранения базы: {e}")

# Проверка прав администратора
def is_admin(message: types.Message):
    return message.from_user and message.from_user.id == ADMIN_ID

# Получение имени автора
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


# ==================== КОМАНДЫ ВЫВОДА СПИСКОВ ====================

@dp.message(F.text.regexp(r'(?i)^!ангелы(\s|$)'))
async def show_elite_list(message: types.Message):
    data = load_data()
    clean_elite = [str(x) for x in data["elite"] if x and isinstance(x, str)]
    elite_str = ", ".join(clean_elite) if clean_elite else "Пусто"
    text = f"👑 <b>Список неприкасаемой элиты чата:</b>\n\n{elite_str}"
    await message.reply(text, parse_mode="HTML")

@dp.message(F.text.regexp(r'(?i)^!список(\s|$)'))
async def show_list(message: types.Message):
    data = load_data()
    clean_pencil = [str(x) for x in data["pencil"] if x and isinstance(x, str)]
    clean_forever = [str(x) for x in data["forever"] if x and isinstance(x, str)]
    
    pencil_str = ", ".join(clean_pencil) if clean_pencil else "Пусто"
    forever_str = ", ".join(clean_forever) if clean_forever else "Пусто"
    
    text = (
        "<b>Список пидерасов, которых я ненавижу:</b>\n\n"
        f"✏️ <b>Карандашиком:</b>\n{pencil_str}\n\n"
        f"🔒 <b>Навсегда:</b>\n{forever_str}"
    )
    await message.reply(text, parse_mode="HTML")


# ==================== КОМАНДЫ УПРАВЛЕНИЯ (РЕПЛАЙ) ====================

@dp.message(F.reply_to_message & F.text.icontains("!элита"))
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

@dp.message(F.reply_to_message & (F.text.icontains("!тетрадка") | F.text.icontains("!пидор")))
async def add_to_list(message: types.Message):
    if not is_admin(message):
        return
        
    username = get_comment_author_name(message.reply_to_message)
    if username in ["Telegram", "Неизвестный нарушитель"] and message.reply_to_message.from_user:
        username = str(message.reply_to_message.from_user.full_name)

    data = load_data()
    if username in data["elite"]:
        await message.reply("Этого пользователя нельзя добавить в тетрадку, он в списке элиты! 👑")
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

@dp.message(F.reply_to_message & F.text.icontains("!удалить"))
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
