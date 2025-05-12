import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import subprocess
import os
import re
import uuid

API_TOKEN = os.getenv("BOT_TOKEN")  # Fly.io tokeni ENV dan olinadi

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

user_links = {}
LINK_REGEX = r'https?://[^\s]+'

@dp.message_handler(commands=['start'])
async def welcome(msg: types.Message):
    await msg.reply("🎬 YouTube, TikTok, Instagram, Facebook yoki X (Twitter) link yuboring.\nMen video formatlarini ko‘rsataman.")

@dp.message_handler(lambda msg: re.match(LINK_REGEX, msg.text))
async def process_link(msg: types.Message):
    url = msg.text.strip()
    user_links[msg.from_user.id] = url

    await msg.reply("🔍 Formatlar olinmoqda...")

    try:
        result = subprocess.run(
            ["yt-dlp", "-F", url],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        output = result.stdout
        lines = output.splitlines()
        buttons = []

        for line in lines:
            if "mp4" in line and "audio only" not in line:
                parts = line.strip().split()
                if len(parts) >= 3:
                    format_id = parts[0]
                    resolution = parts[2]
                    text = f"{resolution} ({format_id})"
                    buttons.append(InlineKeyboardButton(text, callback_data=format_id))

        if not buttons:
            return await msg.reply("❌ Hech qanday video format topilmadi.")

        keyboard = InlineKeyboardMarkup(row_width=2)
        keyboard.add(*buttons[:20])
        await msg.reply("📥 Qaysi formatda yuklaymiz?", reply_markup=keyboard)

    except Exception as e:
        await msg.reply(f"❌ Format olishda xatolik:\n{e}")

@dp.callback_query_handler(lambda c: True)
async def download_selected_format(call: types.CallbackQuery):
    await call.answer()
    user_id = call.from_user.id
    url = user_links.get(user_id)
    format_id = call.data
    filename = f"video_{uuid.uuid4().hex[:8]}.mp4"

    if not url:
        return await call.message.answer("❗ Avval video link yuboring.")

    await call.message.answer("⏳ Yuklab olinmoqda...")

    try:
        subprocess.run(["yt-dlp", "-f", format_id, "-o", filename, url], check=True)

        with open(filename, 'rb') as video:
            await call.message.answer_video(video, caption="✅ Tayyor!")

    except Exception as e:
        await call.message.answer(f"❌ Yuklashda xatolik:\n{e}")

    finally:
        if os.path.exists(filename):
            os.remove(filename)
        user_links.pop(user_id, None)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
