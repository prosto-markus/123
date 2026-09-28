import asyncio
import json
import os

from aiogram import Bot, Dispatcher, F, types
from aiohttp import web

TOKEN = "8905219706:AAEhUewTdjcom8ofzKraGs8F-jTX4_HZ9Sw"
ADMIN_ID = 1737246390

bot = Bot(TOKEN)
dp = Dispatcher()

DATA_FILE = "pidor_list.json"


def load_data():
    if not os.path.exists(DATA_FILE):
        return {
            "pencil": [],
            "forever": [],
            "elite": []
        }

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {
            "pencil": [],
            "forever": [],
            "elite": []
        }


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def is_admin(message: types.Message):
    return message.from_user and message.from_user.id == ADMIN_ID


def get_name(msg: types.Message):
    if msg.from_user:
        if msg.from_user.username:
            return f"@{msg.from_user.username}"
        return msg.from_user.full_name

    return "Неизвестный"


# =========================
# СПИСОК ЭЛИТЫ
# =========================

@dp.message(F.text)
async def text_handler(message: types.Message):

    text = message.text.strip().lower()

    if text == "!ангелы":

        data = load_data()

        if data["elite"]:
            elite = "\n".join(data["elite"])
        else:
            elite = "Пусто"

        await message.reply(
            f"👑 Список неприкасаемой элиты чата:\n\n{elite}"
        )

        return

    if text == "!список":

        data = load_data()

        pencil = "\n".join(data["pencil"]) if data["pencil"] else "Пусто"
        forever = "\n".join(data["forever"]) if data["forever"] else "Пусто"

        await message.reply(
            "📖 Список пидорасов:\n\n"
            f"✏️ Карандашиком:\n{pencil}\n\n"
            f"🔒 Навсегда:\n{forever}"
        )

        return

    if not message.reply_to_message:
        return

    if not is_admin(message):
        return

    username = get_name(message.reply_to_message)

    # =========================
    # ЭЛИТА
    # =========================

    if text == "!элита":

        data = load_data()

        if username in data["elite"]:
            await message.reply(
                f"{username} уже в элите 👑"
            )
            return

        if username in data["pencil"]:
            data["pencil"].remove(username)

        if username in data["forever"]:
            data["forever"].remove(username)

        data["elite"].append(username)

        save_data(data)

        await message.reply(
            f"{username} добавлен в список элиты 👑"
        )

        return

    # =========================
    # ТЕТРАДКА
    # =========================

    if text in ["!тетрадка", "!пидор"]:

        data = load_data()

        if username in data["elite"]:
            await message.reply(
                "Этого пользователя нельзя занести в тетрадку 👑"
            )
            return

        if username in data["forever"]:
            await message.reply(
                f"{username} уже навсегда в тетрадке 🗿"
            )
            return

        if username in data["pencil"]:

            data["pencil"].remove(username)
            data["forever"].append(username)

            save_data(data)

            await message.reply(
                f"{username} теперь в тетрадке навсегда 🔒"
            )

        else:

            data["pencil"].append(username)

            save_data(data)

            await message.reply(
                f"{username} добавлен карандашиком ✏️"
            )

        return

    # =========================
    # УДАЛИТЬ
    # =========================

    if text == "!удалить":

        data = load_data()

        if username in data["pencil"]:

            data["pencil"].remove(username)

            save_data(data)

            await message.reply(
                f"{username} удалён из тетрадки 🧽"
            )

        elif username in data["forever"]:

            await message.reply(
                "Этого уже не стереть 🗿"
            )

        else:

            await message.reply(
                "Этого пользователя нет в карандашной версии списка"
            )


async def handle(request):
    return web.Response(text="Bot is running")


async def main():
    app = web.Application()
    app.router.add_get("/", handle)

    runner = web.AppRunner(app)
    await runner.setup()

    port = int(os.environ.get("PORT", 10000))

    site = web.TCPSite(
        runner,
        "0.0.0.0",
        port
    )

    await site.start()

    print("Бот запущен")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
