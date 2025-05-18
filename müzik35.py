import os
import asyncio
from pyrogram import Client, filters
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped
from yt_dlp import YoutubeDL

API_ID = 24302768  # kendi api_id
API_HASH = "7082b3b3331e7d12971ea9ef19e2d58b"  # kendi api_hash
SESSION_STRING = "1BJWap1sBu3T98i3eNod4zzbROmuXIWsdQJgm9wJjS_JwCi0ts2_XXHX-ei3QN0..."  # kendi session string

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

app = Client(session_string=SESSION_STRING, api_id=API_ID, api_hash=API_HASH)
pytg = PyTgCalls(app)

@pytg.on_stream_end()
async def on_stream_end(_, update):
    # İstersen buraya şarkı bittiğinde yapılacaklar ekleyebilirsin.
    pass

@app.on_message(filters.command("oynat") & filters.group)
async def oynat(client, message):
    if len(message.command) < 2:
        await message.reply("Lütfen bir şarkı adı veya linki yaz.")
        return

    arama = " ".join(message.command[1:])
    status = await message.reply("🎵 Şarkı aranıyor ve indiriliyor...")
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": f"{DOWNLOAD_DIR}/%(title)s.%(ext)s",
        "quiet": True,
        "no_warnings": True,
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(arama, download=True)
        dosya_yolu = ydl.prepare_filename(info)

    await status.edit("🔊 Şarkı sesli sohbette çalınıyor...")
    chat_id = message.chat.id

    await pytg.join_group_call(chat_id, AudioPiped(dosya_yolu))
    await status.edit(f"✅ Şarkı çalınıyor: {info.get('title')}")

@app.on_message(filters.command("durdur") & filters.group)
async def durdur(client, message):
    chat_id = message.chat.id
    await pytg.leave_group_call(chat_id)
    await message.reply("⏹️ Müzik durduruldu.")

async def main():
    await app.start()
    await pytg.start()
    print("Bot ve PyTgCalls başladı.")
    await idle()

if __name__ == "__main__":
    from pytgcalls import idle
    asyncio.run(main())
