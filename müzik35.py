import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import RPCError
from pyrogram.raw.functions.phone import GetGroupCall
from pyrogram.raw.types import InputGroupCall
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import InputAudioStream
from yt_dlp import YoutubeDL

API_ID = 24302768
API_HASH = '7082b3b3331e7d12971ea9ef19e2d58b'
SESSION_STRING = "BAGa5YYAdF3vlpgG1nhmtFSmWj61ly2wYNkknjlWxJf64z3otCfq7OzQq8Oi3cgI-qEp9eNfRcYs34bdz3m-iAL7inLmj3Nff2KjtxfkSF4HIQUO3R_4JptLAMSbSvgi7srvDm376t6tY-EYof7hiqyKKhamnGFStR29lDVww24yxwas3VcK7FDQrGfBly_irg0zysO0u5ODMHCspqaJO7YTkjedJLa43aU43BEeFvOhn-JHDyM7haIe_EkZ3lgXnx71qPgY9Q7txugr0Z2KQg0mgr1LGYGJpwfxDzubtbCg1WNm7RdTX-EDlh91_yh6gyBlfYIlFtJlNflBLkyaavXyr0y7FgAAAAHCpqMoAA"

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

app = Client(
    "userbot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

pytg = PyTgCalls(app)

@pytg.on_stream_end()
async def on_stream_end(_, update):
    chat_id = update.chat_id
    await pytg.leave_group_call(chat_id)

@app.on_message(filters.command("oynat") & filters.group)
async def oynat(client: Client, message: Message):
    query = message.text.split(maxsplit=1)
    if len(query) < 2:
        await message.reply("🎵 Kullanım: /oynat <şarkı_adı veya youtube_link>")
        return
    song = query[1]

    status = await message.reply("🎧 Şarkı aranıyor ve indiriliyor...")

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f"{DOWNLOAD_DIR}/%(title)s.%(ext)s",
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(song, download=True)
            filepath = ydl.prepare_filename(info)
            # mp3 olarak değiştiği için uzantıyı değiştir
            filepath = os.path.splitext(filepath)[0] + ".mp3"
    except Exception as e:
        await status.edit(f"❌ Şarkı indirilemedi: {e}")
        return

    await status.edit("🔊 Sesli sohbete bağlanılıyor...")

    try:
        await pytg.join_group_call(
            message.chat.id,
            InputAudioStream(filepath),
            stream_type=1  # StreamType().pulse_stream = 1
        )
        await status.edit("✅ Şarkı çalınıyor!")
    except Exception as e:
        await status.edit(f"❌ Sesli sohbete bağlanırken hata: {e}")

@app.on_message(filters.command("durdur") & filters.group)
async def durdur(client: Client, message: Message):
    try:
        await pytg.leave_group_call(message.chat.id)
        await message.reply("⏹️ Müzik durduruldu.")
    except Exception as e:
        await message.reply(f"❌ Durdurulurken hata: {e}")

async def main():
    await app.start()
    await pytg.start()
    print("Bot ve PyTgCalls başladı.")
    await app.idle()

if __name__ == "__main__":
    asyncio.run(main())
