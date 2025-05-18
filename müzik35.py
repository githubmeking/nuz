import os
from telethon import TelegramClient, events
from pytgcalls import PyTgCalls
from pytgcalls import idle
from pytgcalls.types import Update
from pytgcalls.types.stream import StreamAudioEnded
from pytgcalls.types.input_stream import InputStream, AudioPiped
from yt_dlp import YoutubeDL

API_ID = 24302768
API_HASH = "7082b3b3331e7d12971ea9ef19e2d58b"
SESSION_STRING = "BAGa5YYAnBEYEjNFsWaE3eVlqtpVlSt0qE0OyFxqrV507d-fNuQgWzMfwMx8AQfMYCVp2l9DO6hQdvonly0PgvlSFIVdYOBLKeQPhAoY7mOgZT4JK-IDkJOm58rHrRV4XtUsbv5Km_iiQ683vvPGJZUKfrqVxVgTqMNenQ-bieTU71aacKEVM6VpGCcRxmYONxHZ-QX5BN6J6Eebo_AfIjThJxl96dyIPXyMieu5WmoMAcgW23lOjo5pNTIICtVvmdFhNdd5X5Kp0m_3hIwqJMwC1gm1DzXR9mDWZJij1GpNpQA8MpENCuOSTlsLACZjwtyUSLHc19vmvE1U_Bp0k8BftCXcqwAAAAHCpqMoAA"

client = TelegramClient("userbot", API_ID, API_HASH).start(session=SESSION_STRING)
pytgcalls = PyTgCalls(client)

@client.on(events.NewMessage(pattern=r"/oynat (.+)"))
async def oynat(event):
    chat_id = event.chat_id
    query = event.pattern_match.group(1)
    await event.reply("Şarkı aranıyor...")
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'song.%(ext)s',
        'noplaylist': True
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=True)
        file_path = ydl.prepare_filename(info)
    await event.reply("Şarkı çalınıyor...")
    await pytgcalls.join_group_call(
        chat_id,
        AudioPiped(file_path)
    )

@client.on(events.NewMessage(pattern=r"/durdur"))
async def durdur(event):
    chat_id = event.chat_id
    await pytgcalls.leave_group_call(chat_id)
    await event.reply("Durduruldu.")

async def main():
    await pytgcalls.start()
    print("Bot başlatıldı.")
    await idle()

with client:
    client.loop.run_until_complete(main())
