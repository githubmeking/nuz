import os
from pyrogram import Client, filters
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import InputStream, AudioPiped
from yt_dlp import YoutubeDL
import asyncio

API_ID = 24302768
API_HASH = "7082b3b3331e7d12971ea9ef19e2d58b"
SESSION_STRING = "BURAYA_PYROGRAM_SESSION_STRING_YAPIŞTIR"   # <-- yukarıdan aldığın string!

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

app = Client(SESSION_STRING, api_id=API_ID, api_hash=API_HASH)
pytgcalls = PyTgCalls(app)

@app.on_message(filters.command("oynat") & filters.group)
async def play_handler(client, message):
    if len(message.command) < 2:
        await message.reply("Lütfen bir şarkı ismi veya YouTube linki girin.")
        return
    query = " ".join(message.command[1:])
    status = await message.reply("🎵 Şarkı aranıyor ve indiriliyor...")
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
        'noplaylist': True,
        'quiet': True,
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=True)
        file_path = ydl.prepare_filename(info)
    await status.edit("🔊 Şarkı sesli sohbette çalınıyor...")
    chat_id = message.chat.id
    await pytgcalls.join_group_call(
        chat_id,
        AudioPiped(file_path)
    )
    await status.edit("✅ Şarkı çalıyor!")

@app.on_message(filters.command("durdur") & filters.group)
async def stop_handler(client, message):
    await pytgcalls.leave_group_call(message.chat.id)
    await message.reply("⏹️ Müzik durduruldu.")

async def main():
    await app.start()
    await pytgcalls.start()
    print("Bot ve PyTgCalls başladı.")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
