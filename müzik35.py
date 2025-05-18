from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls import PyTgCalls, idle
from pytgcalls.types.input_stream import InputStream, AudioPiped
from yt_dlp import YoutubeDL
import os

API_ID = 123456  # API ID (my.telegram.org)
API_HASH = "abcdef1234567890abcdef1234567890"  # API Hash (my.telegram.org)
SESSION_STRING = ""  # Userbot string session (telethon/pyrogramdan oluştur)

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

app = Client(session_name=SESSION_STRING, api_id=API_ID, api_hash=API_HASH, in_memory=True)
call = PyTgCalls(app)

@app.on_message(filters.command("oynat", prefixes="/") & filters.group)
async def play(_, message: Message):
    if len(message.command) < 2:
        return await message.reply("Kullanım: /oynat <şarkı adı veya YouTube linki>")
    query = " ".join(message.command[1:])
    status = await message.reply("🎵 Şarkı aranıyor ve indiriliyor...")
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s"),
        "quiet": True,
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=True)
        file_path = ydl.prepare_filename(info)
    await status.edit("🔊 Şarkı sesli sohbette çalınıyor...")
    await call.join_group_call(
        message.chat.id,
        InputStream(
            AudioPiped(file_path)
        )
    )
    await status.edit("✅ Şarkı çalıyor!")

@app.on_message(filters.command("durdur", prefixes="/") & filters.group)
async def stop(_, message: Message):
    await call.leave_group_call(message.chat.id)
    await message.reply("⏹️ Müzik durduruldu.")

async def main():
    await app.start()
    await call.start()
    print("Bot başladı!")
    await idle()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
