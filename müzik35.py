import os
import asyncio
from pyrogram import Client, filters
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import AudioPiped
from yt_dlp import YoutubeDL

API_ID = 24302768
API_HASH = "7082b3b3331e7d12971ea9ef19e2d58b"
SESSION_STRING = "BAGa5YYAdF3vlpgG1nhmtFSmWj61ly2wYNkknjlWxJf64z3otCfq7OzQq8Oi3cgI-qEp9eNfRcYs34bdz3m-iAL7inLmj3Nff2KjtxfkSF4HIQUO3R_4JptLAMSbSvgi7srvDm376t6tY-EYof7hiqyKKhamnGFStR29lDVww24yxwas3VcK7FDQrGfBly_irg0zysO0u5ODMHCspqaJO7YTkjedJLa43aU43BEeFvOhn-JHDyM7haIe_EkZ3lgXnx71qPgY9Q7txugr0Z2KQg0mgr1LGYGJpwfxDzubtbCg1WNm7RdTX-EDlh91_yh6gyBlfYIlFtJlNflBLkyaavXyr0y7FgAAAAHCpqMoAA"

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

app = Client(session_string=SESSION_STRING, api_id=API_ID, api_hash=API_HASH)
pytg = PyTgCalls(app)


@app.on_message(filters.command("oynat") & filters.group)
async def oynat(client, message):
    query = " ".join(message.command[1:])
    if not query:
        await message.reply("Lütfen çalmak istediğin şarkının YouTube linkini veya ismini yaz.")
        return

    status_msg = await message.reply("🎵 Şarkı indiriliyor, lütfen bekleyin...")

    ydl_opts = {
        "format": "bestaudio",
        "outtmpl": os.path.join(DOWNLOAD_DIR, "%(id)s.%(ext)s"),
        "quiet": True,
        "no_warnings": True,
    }
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=True)
            file_path = ydl.prepare_filename(info)
    except Exception as e:
        await status_msg.edit(f"⚠️ Şarkı indirilemedi: {e}")
        return

    await status_msg.edit("🔊 Şarkı sesli sohbette çalınıyor...")

    try:
        await pytg.join_group_call(
            message.chat.id,
            AudioPiped(file_path)
        )
        await status_msg.edit("✅ Şarkı çalıyor!")
    except Exception as e:
        await status_msg.edit(f"⚠️ Sesli sohbete katılamadı: {e}")


@app.on_message(filters.command("durdur") & filters.group)
async def durdur(client, message):
    try:
        await pytg.leave_group_call(message.chat.id)
        await message.reply("⏹️ Müzik durduruldu.")
    except Exception as e:
        await message.reply(f"⚠️ Müzik durdurulamadı: {e}")


async def main():
    await app.start()
    await pytg.start()
    print("Bot ve PyTgCalls başladı.")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
