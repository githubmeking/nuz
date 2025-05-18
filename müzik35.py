import os
from pyrogram import Client, filters
from pytgcalls import PyTgCalls, idle
from pytgcalls.types.input_stream import InputStream, InputAudioStream
from yt_dlp import YoutubeDL

API_ID = 24302768
API_HASH = "7082b3b3331e7d12971ea9ef19e2d58b"
SESSION_STRING = "1BJWap1sBu6j8lRL81uy0gXrZstXa4Iey2JGcu7R4UTNYMAPysVUOlnZj8lzNfqDV0dvk4XIBsvjKmSRBNQBneewkZewFtS2GrDn7lEqzMNERcX2ifCt7NQKHRFGEUMnAvTykgOyE4k88QXiI5bzWkOS5zuEba2ULZkwgxRw3-YROrTEloWoluqpJ48VavgfvehlPyrVCMuoOAT6EYr7rp6JN7zWWjo11voDd8sqini9nkFtQh_mmgT_vqHGV_Ge78NwBTXq35EAiGSEhnA7u9GvSn1V-V-BN_yrUwCHbVm5gXo_GTi3ZgGrIs-JUva6q6dl2amhHRyfuBC96H_iOXwr3hr2AKzs="

DOWNLOADS = "downloads"
os.makedirs(DOWNLOADS, exist_ok=True)

app = Client(session_string=SESSION_STRING, api_id=API_ID, api_hash=API_HASH)
call = PyTgCalls(app)

@call.on_stream_end()
async def _(client, update):
    await call.leave_group_call(update.chat_id)

@app.on_message(filters.command("oynat") & filters.group)
async def oynat(_, message):
    if len(message.command) < 2:
        await message.reply("Kullanım: `/oynat <şarkı adı veya link>`", quote=True)
        return
    await message.reply("Şarkı aranıyor ve indiriliyor...", quote=True)
    query = " ".join(message.command[1:])
    ydl_opts = {
        'format': 'bestaudio',
        'outtmpl': f'{DOWNLOADS}/%(title)s.%(ext)s',
        'quiet': True,
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=True)
        file_path = ydl.prepare_filename(info)
    await call.join_group_call(
        message.chat.id,
        InputAudioStream(file_path)
    )
    await message.reply(f"Çalıyor: {info['title']}", quote=True)

@app.on_message(filters.command("durdur") & filters.group)
async def durdur(_, message):
    await call.leave_group_call(message.chat.id)
    await message.reply("Müzik durduruldu.", quote=True)

async def main():
    await app.start()
    await call.start()
    print("Bot aktif!")
    await idle()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
