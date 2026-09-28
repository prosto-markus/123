import asyncio
import os
import re
from aiogram import Bot, Dispatcher, types, F
from aiohttp import web, ClientSession

# 1. ТОКЕН БОТА:
TOKEN = "8905219706:AAEhUewTdjcom8ofzKraGs8F-jTX4_HZ9Sw"

# 2. Вкажіть ваші ID:
ADMIN_ID = 1737246390
CHANNEL_ID = -1003506217494

# 3. Ключі JSONBin:
JSONBIN_BIN_ID = "6ab9fb53ffd5d1605336756f"
JSONBIN_KEY = "$2a$10$6QcyxPOAJ1Lsu5wSqN1YBur2XtSPujA43PrX2/KqjRS33J6Y2ylaW"
JSONBIN_URL = f"https://api.jsonbin.io/v3/b/{JSONBIN_BIN_ID}"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Завантаження даних з хмари
async def load_data():
    headers = {
        "X-Master-Key": JSONBIN_KEY,
        "X-Bin-Meta": "false"
    }
    try:
        clean_url = JSONBIN_URL.replace("/latest", "")
        url = f"{clean_url}/latest"
        async with ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if not isinstance(data, dict): data = {}
                    if "pencil" not in data or not isinstance(data["pencil"], list): data["pencil"] = []
                    if "forever" not in data or not isinstance(data["forever"], list): data["forever"] = []
                    if "elite" not in data or not isinstance(data["elite"], list): data["elite"] = []
                    return data
                else:
                    print(f"Помилка завантаження JSONBin: {resp.status}")
    except Exception as e:
        print(f"Помилка завантаження з хмари: {e}")
    return {"pencil": [], "forever": [], "elite": []}

# Збереження даних у хмару
async def save_data(data):
    clean_url = JSONBIN_URL.replace("/latest", "")
    headers = {
        "Content-Type": "application/json",
        "X-Master-Key": JSONBIN_KEY,
        "X-Bin-Versioning": "false"
    }
    try:
        async with ClientSession() as session:
            async with session.put(clean_url, json=data, headers=headers) as resp:
                if resp.status != 200:
                    print(f"Помилка збереження JSONBin: {resp.status}")
                else:
                    print("Дані успішно збережено в JSONBin!")
    except Exception as e:
        print(f"Помилка з'єднання з хмарою: {e}")

# Перевірка адміна (особистий акаунт або канал)
def is_admin(message: types.Message) -> bool:
    if message.from_user and message.from_user.id == ADMIN_ID:
        return True
    if message.sender_chat and message.sender_chat.id == CHANNEL_ID:
        return True
    return False

# Отримання імені автора
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


# ==================== ВИВІД СПИСКІВ ====================

@dp.message(F.text.regexp(r'(?i)^!эй(\s|$)'))
async def show_elite_list(message: types.Message):
    data = await load_data()
    clean_elite = [str(x) for x in data["elite"] if x and isinstance(x, str)]
    elite_str = ", ".join(clean_elite) if clean_elite else "Пусто"
    text = f"👑 <b>Список неприкасаемой элиты чата:</b>\n\n{elite_str}"
    await message.reply(text, parse_mode="HTML")

@dp.message(F.text.regexp(r'(?i)^!список(\s|$)'))
async def show_list(message: types.Message):
    data = await load_data()
    clean_pencil = [str(x) for x in data["pencil"] if x and isinstance(x, str)]
    clean_forever = [str(x) for x in data["forever"] if x and isinstance(x, str)]
    
    pencil_str = ", ".join(clean_pencil) if clean_pencil else "Пусто"
    forever_str = ", ".join(clean_forever) if clean_forever else "Пусто"
    
    text = (
        "<b>Список пидорасов, которых я ненавижу:</b>\n\n"
        f"✏️ <b>Карандашиком:</b>\n{pencil_str}\n\n"
        f"🔒 <b>Навсегда:</b>\n{forever_str}"
    )
    await message.reply(text, parse_mode="HTML")


# ==================== УПРАВЛІННЯ ЧЕРЕЗ РЕПЛАЙ ====================

@dp.message(F.reply_to_message & F.text.regexp(r'(?i)^!элита(\s|$)'))
async def add_to_elite(message: types.Message):
    if not is_admin(message):
        await message.reply("❌ У вас нет прав для использования этой команды. Идите, пожалуйста, нахуй")
        return
        
    username = get_comment_author_name(message.reply_to_message)
    data = await load_data()
    
    if username in data["elite"]:
        await message.reply(f"{username} уже находится в списке элиты. ✨")
        return
        
    if username in data["pencil"]: data["pencil"].remove(username)
    if username in data["forever"]: data["forever"].remove(username)
        
    data["elite"].append(username)
    await save_data(data)
    await message.reply(f"{username} добавлен в список элиты! 👑 Его больше нельзя занести в тетрадку.")

@dp.message(F.reply_to_message & F.text.regexp(r'(?i)^(!тетрадка|!пидор)(\s|$)'))
async def add_to_list(message: types.Message):
    if not is_admin(message):
        await message.reply("❌ У вас нет прав для использования этой команды.")
        return
        
    username = get_comment_author_name(message.reply_to_message)
    data = await load_data()
    
    if username in data["elite"]:
        await message.reply("Этого пользователя хуй добавишь в тетрадку, он в списке элиты! 👑")
        return
    if username in data["forever"]:
        await message.reply(f"{username} уже в тетрадке пидорасов навсегда. Тут без шансов.")
        return
        
    if username in data["pencil"]:
        data["pencil"].remove(username)
        data["forever"].append(username)
        await save_data(data)
        await message.reply(f"{username} в тетрадке пидорасов навсегда. ⛔")
    else:
        data["pencil"].append(username)
        await save_data(data)
        await message.reply(f"{username} в тетрадке пидорасов, но пока карандашиком. ✏️")

@dp.message(F.reply_to_message & F.text.regexp(r'(?i)^!удалить(\s|$)'))
async def remove_from_pencil(message: types.Message):
    if not is_admin(message):
        await message.reply("❌ У вас нет прав для использования этой команды.")
        return
        
    username = get_comment_author_name(message.reply_to_message)
    data = await load_data()
    
    if username in data["pencil"]:
        data["pencil"].remove(username)
        await save_data(data)
        await message.reply(f"Стерто. {username} удален из тетрадки карандашиком, на этот раз прощаю")
    elif username in data["forever"]:
        await message.reply("Этого уже не стереть, он в тетрадке навсегда. Пидорасом родился, им же и умрет")
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
    
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
