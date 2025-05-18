import os
import re
import asyncio
from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument

api_id = 20213849
api_hash = 'e97df0eca2a9531c80202c1a7d3f5721'
HEDEF_GRUP_LINK = "https://t.me/+q5Ui3I8HNMwxYTM8"

downloads_dir = 'downloads'
if not os.path.exists(downloads_dir):
    os.makedirs(downloads_dir)

client = TelegramClient('userbot_session', api_id, api_hash)
downloading = {}
progress_last_update = {}

def format_size(size_in_bytes):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_in_bytes < 1024:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024
    return f"{size_in_bytes:.2f} TB"

def extract_channel_and_message_id(link):
    if link.startswith("https://t.me/c/"):
        m = re.match(r"https://t.me/c/(\d+)/(\d+)", link)
        if m:
            channel_id = int(f"-100{m.group(1)}")
            message_id = int(m.group(2))
            return channel_id, message_id
    elif link.startswith("https://t.me/"):
        parts = link.rstrip('/').split('/')
        if len(parts) >= 5:
            username = parts[3]
            try:
                message_id = int(parts[4])
            except:
                return None, None
            return username, message_id
    return None, None

async def resolve_group_id(link_or_username):
    try:
        entity = await client.get_entity(link_or_username)
        return entity.id
    except Exception as e:
        print(f"Grup ID alınamadı: {e}")
        return None

async def progress_callback(current, total, status_msg, file_name):
    now = asyncio.get_event_loop().time()
    last_update = progress_last_update.get(file_name, 0)
    if now - last_update < 2 and current != total:
        return
    progress_last_update[file_name] = now
    percentage = (current / total * 100) if total else 0
    downloaded_size = format_size(current)
    total_size = format_size(total) if total else "?"
    msg_text = (
        f"⬇️ **{file_name}** indiriliyor...\n"
        f"İlerleme: **{percentage:.2f}%**\n"
        f"İndirilen: **{downloaded_size}** / Toplam: **{total_size}**"
    )
    try:
        await status_msg.edit(msg_text)
    except Exception:
        pass
    print(f"{file_name}: {percentage:.2f}% | {downloaded_size}/{total_size}")

async def download_and_forward(channel, start_message_id, hedef_grup_id):
    last_id = start_message_id
    downloading[channel] = True
    print(f"TAŞIMA BAŞLADI | Kaynak: {channel} | Başlangıç mesajı: {start_message_id}")
    while downloading.get(channel, False):
        found_any = False
        try:
            async for message in client.iter_messages(channel, min_id=last_id, reverse=True):
                if message.media:
                    found_any = True
                    if isinstance(message.media, MessageMediaPhoto):
                        file_name = f"photo_{message.id}.jpg"
                    elif isinstance(message.media, MessageMediaDocument):
                        file_name = next((a.file_name for a in message.media.document.attributes if hasattr(a, 'file_name')), f"doc_{message.id}")
                    else:
                        file_name = f"media_{message.id}"
                    file_path = os.path.join(downloads_dir, file_name)
                    try:
                        status_msg = await client.send_message('me', f"⬇️ {file_name} indiriliyor...")
                        downloaded = await message.download_media(
                            file_path,
                            progress_callback=lambda c, t: asyncio.ensure_future(progress_callback(c, t, status_msg, file_name))
                        )
                        file_size = os.path.getsize(downloaded)
                        caption = message.text or ""
                        await client.send_file(hedef_grup_id, downloaded, caption=caption)
                        await status_msg.edit(f"✅ {file_name} gönderildi ({format_size(file_size)}).")
                        print(f"GÖNDERİLDİ: {file_name} ({format_size(file_size)})")
                        os.remove(downloaded)
                    except Exception as e:
                        await client.send_message('me', f"Hata ({file_name}): {e}")
                        print(f"HATA ({file_name}): {e}")
                    last_id = max(last_id, message.id)
            await asyncio.sleep(5)
            if not found_any:
                await asyncio.sleep(10)
        except Exception as err:
            await client.send_message('me', f"Genel döngü hatası: {err}")
            print(f"GENEL DÖNGÜ HATASI: {err}")
            await asyncio.sleep(10)

@client.on(events.NewMessage(pattern=r'/indir (.+)'))
async def start_download(event):
    link = event.pattern_match.group(1)
    channel, start_id = extract_channel_and_message_id(link)
    if not channel or not start_id:
        await event.reply("Linkten kanal ve mesaj ID'si çözülemedi. Lütfen tam link gönder.")
        return
    if downloading.get(channel, False):
        await event.reply("Bu kanalda zaten aktif bir indirme/taşıma işlemi var.")
        return
    hedef_grup_id = await resolve_group_id(HEDEF_GRUP_LINK)
    if not hedef_grup_id:
        await event.reply("Hedef grup linkinden grup ID'si alınamadı!")
        return
    await event.reply("TAŞIMA BAŞLATILDI: Her medya indirildikçe hedef gruba aktarılacak.")
    asyncio.create_task(download_and_forward(channel, start_id, hedef_grup_id))

@client.on(events.NewMessage(pattern=r'/durdur (.+)'))
async def stop_download(event):
    link = event.pattern_match.group(1)
    channel, _ = extract_channel_and_message_id(link)
    if channel in downloading:
        downloading[channel] = False
        await event.reply("İşlem durduruldu.")
    else:
        await event.reply("Bu kanal için aktif bir işlem yok.")

async def main():
    print("Telefon numaranızı +90 şeklinde girin:")
    phone = input("Telefon: ")

    await client.connect()
    if not await client.is_user_authorized():
        sent = await client.send_code_request(phone)
        code = input("Telegram'dan gelen kodu girin: ")
        await client.sign_in(phone, code, phone_code_hash=sent.phone_code_hash)
    print("Giriş başarılı!")

    print("Bot hazır. Telegram'da kendinize /indir <mesaj_linki> gönderebilirsiniz.")
    await client.run_until_disconnected()

if __name__ == '__main__':
    with client:
        client.loop.run_until_complete(main())
