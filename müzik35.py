from telethon import TelegramClient, events
from telethon.sessions import StringSession
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import AudioPiped

API_ID = 24302768
API_HASH = "7082b3b3331e7d12971ea9ef19e2d58b"
SESSION_STRING = "1BJWap1sBu3T98i3eNod4zzbROmuXIWsdQJgm9wJjS_JwCi0ts2_XXHX-ei3QN0-ePVOkxi1eIhSqwSjeGajn0TTVjr1SgVoxQFc_bag8KBTLm9cWoEanWuohS2tLvMXeCndY3VhGAyA8CH9z2Zqht15d36i9UOEBwxxCEBhEuTIMrCnw-Pjy56Dxl0I8TXjU_BpncaMGOpwN6r36_QydSyV1n-TyTTujK1HnQZg7Y-5JMxF11BXP93MvsSC3zCsHmzyen-dWELV2e6vcTaJpigh4smlT3biQosVJ3ZOJ-svpStg2U1IYahirl7Xnlycw2JJWOUkMw9RJfQfr66f1jUP7sOeHQPg="

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
pytg = PyTgCalls(client)

@client.on(events.NewMessage(pattern='/oynat (.+)'))
async def oynat(event):
    chat_id = event.chat_id
    song_path = "test.mp3"  # test.mp3 dosyası aynı dizinde olmalı!
    await pytg.join_group_call(
        chat_id,
        AudioPiped(song_path)
    )
    await event.reply("Şarkı çalınıyor!")

@client.on(events.NewMessage(pattern='/durdur'))
async def durdur(event):
    await pytg.leave_group_call(event.chat_id)
    await event.reply("Çalma durduruldu!")

async def main():
    await client.start()
    await pytg.start()
    print("Bot hazır!")
    await client.run_until_disconnected()

import asyncio
if __name__ == "__main__":
    asyncio.run(main())
