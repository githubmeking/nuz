import asyncio
import os
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from pytgcalls import PyTgCalls, idle
from pytgcalls.types import Update
from pytgcalls.types.stream import StreamAudioEnded
from pytgcalls.types.input_stream import InputStream, AudioPiped
from yt_dlp import YoutubeDL

API_ID = 1234567  # BURAYA api_id
API_HASH = "api_hash_buraya"
SESSION_STRING = "BAGa5YYAnBEYEjNFsWaE3eVlqtpVlSt0qE0OyFxqrV507d-fNuQgWzMfwMx8AQfMYCVp2l9DO6hQdvonly0PgvlSFIVdYOBLKeQPhAoY7mOgZT4JK-IDkJOm58rHrRV4XtUsbv5Km_iiQ683vvPGJZUKfrqVxVgTqMNenQ-bieTU71aacKEVM6VpGCcRxmYONxHZ-QX5BN6J6Eebo_AfIjThJxl96dyIPXyMieu5WmoMAcgW23lOjo5pNTIICtVvmdFhNdd5X5Kp0m_3hIwqJMwC1gm1DzXR9mDWZJij1GpNpQA8MpENCuOSTlsLACZjwtyUSLHc19vmvE1U_Bp0k8BftCXcqwAAAAHCpqMoAA"

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
pytgcalls = PyTgCalls(client)

@client.on(events.NewMessage(pattern=r"/oynat (.+)"))
async def handler(event):
    if event.is_private:
        await event.reply("Lütfen bir grup veya kanalda kullanın.")
        return
    msg = await event.reply("Şarkı aranıyor ve indiriliyor...")
    song = event.pattern_match.group(1)
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{DOWNLOAD_DIR}/%(title)s.%(ext)s',
        'noplaylist': True,
        'quiet': True,
    }
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{song}", download=True)['entries'][0]
            file_path = ydl.prepare_filename(info)
        await msg.edit("Şarkı indirildi, sesli sohbette çalınıyor...")
        await pytgcalls.join_group_call(
            event.chat_id,
            InputStream(
                AudioPiped(file_path)
            ),
        )
        await msg.edit(f"Çalınıyor: {info['title']}")
    except Exception as e:
        await msg.edit(f"Bir hata oluştu: {e}")

@client.on(events.NewMessage(pattern=r"/durdur"))
async def stop(event):
    await pytgcalls.leave_group_call(event.chat_id)
    await event.reply("Sesli sohbetten ayrıldı, müzik durduruldu.")

# Otomatik şarkı bitince bırak (isteğe bağlı)
@pytgcalls.on_stream_end()
async def on_stream_end(gc, update: StreamAudioEnded):
    await pytgcalls.leave_group_call(update.chat_id)

async def main():
    await client.start()
    await pytgcalls.start()
    print("Bot ve PyTgCalls başladı.")
    await idle()

if __name__ == "__main__":
    asyncio.run(main())
