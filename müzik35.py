from telethon import TelegramClient, events, functions
from telethon.tl.functions.messages import GetForumTopics, CreateForumTopic
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
import os
import re
import asyncio

# --- AYARLAR ---
api_id = 20213849
api_hash = 'e97df0eca2a9531c80202c1a7d3f5721'
HEDEF_GRUP_LINK = "https://t.me/+q5Ui3I8HNMwxYTM8"  # Grup davet linki

client = TelegramClient('userbot_session', api_id, api_hash)

downloads_dir = 'downloads'
if not os.path.exists(downloads_dir):
    os.makedirs(downloads_dir)

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
        topic_pattern = re.match(r"https://t.me/c/(\d+)/(\d+)/(\d+)", link)
        if topic_pattern:
            channel_id = int(f"-100{topic_pattern.group(1)}")
            topic_id = int(topic_pattern.group(2))
            message_id = int(topic_pattern.group(3))
            return channel_id, message_id, topic_id
        m = re.match(r"https://t.me/c/(\d+)/(\d+)", link)
        if m:
            channel_id = int(f"-100{m.group(1)}")
            message_id = int(m.group(2))
            return channel_id, message_id, None
    elif link.startswith("https://t.me/"):
        parts = link.split('/')
        if len(parts) >= 5:
            try:
                msg_id = int(parts[4])
            except Exception:
                return None, None, None
            return parts[3], msg_id, None
    return None, None, None

async def get_topic_name(group_id, topic_id):
    try:
        result = await client(GetForumTopics(
            peer=group_id,
            offset_date=0,
            offset_id=0,
            offset_topic=0,
            limit=100
        ))
        for topic in result.topics:
            if topic.id == topic_id:
                return topic.title
    except Exception as e:
        print(f"Topic adı alınamadı: {e}")
    return None

async def get_or_create_topic(group_id, topic_title):
    if not topic_title:
        topic_title = "Genel"
    try:
        result = await client(GetForumTopics(
            peer=group_id,
            offset_date=0,
            offset_id=0,
            offset_topic=0,
            limit=100
        ))
        for topic in result.topics:
            if topic.title.lower() == topic_title.lower():
                return topic.id
        # Yoksa yeni oluştur
        new_topic = await client(CreateForumTopic(
            peer=group_id,
            title=topic_title
        ))
        return new_topic.topic_id
    except Exception as e:
        print(f"Konu oluşturulamadı: {e}")
    return None

async def resolve_group_id(link):
    try:
        entity = await client.get_entity(link)
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

async def download_and_forward(channel, start_message_id, hedef_grup_id, topic_id=None):
    last_id = start_message_id
    downloading[channel] = True
    print(f"TAŞIMA BAŞLADI | Kaynak: {channel} | Başlangıç mesajı: {start_message_id} | Topic ID: {topic_id}")
    while downloading.get(channel, False):
        found_any = False
        try:
            async for message in client.iter_messages(channel, min_id=last_id, reverse=True):
                if topic_id and hasattr(message, 'topic_id') and message.topic_id != topic_id:
                    continue
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
                        src_topic_id = getattr(message, "topic_id", None)
                        if src_topic_id:
                            src_topic_name = await get_topic_name(channel, src_topic_id)
                        else:
                            src_topic_name = "Genel"
                        dest_topic_id = await get_or_create_topic(hedef_grup_id, src_topic_name)
                        hashtag = f"\n#{src_topic_name.replace(' ', '_')}"
                        caption = (message.text or "") + hashtag
                        await client.send_file(hedef_grup_id, downloaded, caption=caption, topic_id=dest_topic_id)
                        await status_msg.edit(f"✅ {file_name} gönderildi ({format_size(file_size)}).\nKonu: {src_topic_name}")
                        print(f"GÖNDERİLDİ: {file_name} ({format_size(file_size)}) | Hedef konu: {src_topic_name}")
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
    channel, start_id, topic_id = extract_channel_and_message_id(link)
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
    await event.reply("TAŞIMA BAŞLATILDI: Her medya indirildikçe hedef grupta aynı konunun içine aktarılacak.")
    asyncio.create_task(download_and_forward(channel, start_id, hedef_grup_id, topic_id))

@client.on(events.NewMessage(pattern=r'/durdur (.+)'))
async def stop_download(event):
    link = event.pattern_match.group(1)
    channel, _, _ = extract_channel_and_message_id(link)
    if channel in downloading:
        downloading[channel] = False
        await event.reply("İşlem durduruldu.")
    else:
        await event.reply("Bu kanal için aktif bir işlem yok.")

async def main():
    print("Telefon numaranız ile giriş yapınız (örn. +90...)")
    await client.start()
    print("Bot hazır. Telegram'da kendinize /indir <mesaj_linki> gönderebilirsiniz.")
    await client.run_until_disconnected()

if __name__ == '__main__':
    with client:
        client.loop.run_until_complete(main())
