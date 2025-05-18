import asyncio
from pyrogram import Client, filters
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import InputStream, AudioPiped
from yt_dlp import YoutubeDL
import os

API_ID = 24302768
API_HASH = "7082b3b3331e7d12971ea9ef19e2d58b"
SESSION_STRING = "BAGa5YYAnBEYEjNFsWaE3eVlqtpVlSt0qE0OyFxqrV507d-fNuQgWzMfwMx8AQfMYCVp2l9DO6hQdvonly0PgvlSFIVdYOBLKeQPhAoY7mOgZT4JK-IDkJOm58rHrRV4XtUsbv5Km_iiQ683vvPGJZUKfrqVxVgTqMNenQ-bieTU71aacKEVM6VpGCcRxmYONxHZ-QX5BN6J6Eebo_AfIjThJxl96dyIPXyMieu5WmoMAcgW23lOjo5pNTIICtVvmdFhNdd5X5Kp0m_3hIwqJMwC1gm1DzXR9mDWZJij1GpNpQA8MpENCuOSTlsLACZjwtyUSLHc19vmvE1U_Bp0k8BftCXcqwAAAAHCpqMoAA"

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

app = Client(
    SESSION_STRING,
    api_id=API_ID,
    api_hash=API_HASH
)
pytgcalls = PyTgCalls(app)

# /oynat komutu ile şarkı çal
@app.on_message(filters.command("oynat") & filters.group)
async def play(client, message):
    if len(message.command) < 2:
        await message.reply("Kullanım: /oynat <YouTube linki veya şarkı adı>")
        return

    query = " ".join(message.command[1:])
    status = await message.reply("🎵 Şarkı aranıyor ve indiriliyor...")

    # YoutubeDL ile ses dosyasını indir
    ydl_opts = {
        'format': 'bestaudio',
        'outtmpl': f'{DOWNLOAD_DIR}/%(title)s.%(ext)s',
        'noplaylist': True,
        'quiet': True
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=True)
        file_path = ydl.prepare_filename(info)

    await status.edit("🔊 Şarkı sesli sohbette çalınıyor...")

    await pytgcalls.join_group_call(
        message.chat.id,
        AudioPiped(file_path)
    )
    await status.edit("✅ Şarkı çalınıyor!")

# /durdur komutu ile sesi durdur
@app.on_message(filters.command("durdur") & filters.group)
async def stop(client, message):
    await pytgcalls.leave_group_call(message.chat.id)
    await message.reply("⏹️ Müzik durduruldu.")

async def main():
    await app.start()
    await pytgcalls.start()
    print("Bot çalışıyor!")
    await asyncio.get_event_loop().create_future()

if __name__ == "__main__":
    asyncio.run(main())
