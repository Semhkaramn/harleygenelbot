"""
Harley Telegram Bot - Log Bot Modülü
=====================================
Admin log'ları izler ve log grubuna gönderir
"""

import asyncio
import logging
from datetime import datetime

from telethon import events
from telethon.tl.functions.channels import GetAdminLogRequest

from ...utils.helpers import get_user_info, format_date, get_media_info, get_content_text
from .actions import AdminLogActionProcessor
from .formatter import LogFormatter

logger = logging.getLogger(__name__)


class LogBotModule:
    """Log Bot Modülü"""

    def __init__(self, bot, config):
        self.bot = bot
        self.config = config
        self.client = bot.client

        self.last_event_id = 0
        self.message_cache = {}

        self.action_processor = AdminLogActionProcessor(
            client=self.client,
            send_log_callback=self.send_log
        )

        logger.info(f"Log Bot: Kaynak={config.source_group_id}, Log={config.log_group_id}")

    async def start(self):
        """Modülü başlat"""
        logger.info("Log Bot modülü başlatılıyor...")

        source_id = self.config.source_group_id

        # Mesaj cache handler
        self.client.add_event_handler(
            self.cache_new_message,
            events.NewMessage(chats=source_id)
        )

        # Mesaj düzenleme handler
        self.client.add_event_handler(
            self.on_message_edited,
            events.MessageEdited(chats=source_id)
        )

        # Mesaj silme handler
        self.client.add_event_handler(
            self.on_message_deleted,
            events.MessageDeleted(chats=source_id)
        )

        # Chat action handler
        self.client.add_event_handler(
            self.on_chat_action,
            events.ChatAction(chats=source_id)
        )

        # Grup bilgilerini al
        try:
            source = await self.client.get_entity(source_id)
            log_group = await self.client.get_entity(self.config.log_group_id)
            logger.info(f"İzlenen: {source.title}, Log: {log_group.title}")

            await self.send_log(LogFormatter.bot_started(
                source.title,
                self.bot.me.first_name,
                format_date(datetime.now())
            ))
        except Exception as e:
            logger.error(f"Grup bilgisi alınamadı: {e}")

        # Admin log kontrolü başlat
        self.bot.add_task(self.check_admin_log())

        logger.info("Log Bot modülü başlatıldı")

    async def send_log(self, text: str, file=None):
        """Log grubuna mesaj gönder"""
        try:
            await self.client.send_message(
                self.config.log_group_id,
                text,
                file=file,
                link_preview=False,
                parse_mode='md'
            )
            await asyncio.sleep(0.5)  # Rate limit koruması
        except Exception as e:
            error_str = str(e)
            if "A wait of" in error_str and "seconds is required" in error_str:
                import re
                wait_match = re.search(r'wait of (\d+)', error_str)
                wait_time = int(wait_match.group(1)) if wait_match else 30
                logger.warning(f"FloodWait: {wait_time}sn bekleniyor...")
                await asyncio.sleep(wait_time + 1)
                # Tekrar dene
                try:
                    await self.client.send_message(
                        self.config.log_group_id,
                        text,
                        file=file,
                        link_preview=False,
                        parse_mode='md'
                    )
                except Exception as retry_e:
                    logger.error(f"Retry sonrası hata: {retry_e}")
            else:
                logger.error(f"Log gönderme hatası: {e}")

    async def cache_new_message(self, event):
        """Yeni mesajları cache'le"""
        msg = event.message
        self.message_cache[msg.id] = {
            'text': msg.message,
            'media': msg.media,
            'sender_id': msg.sender_id,
            'date': msg.date
        }

        if len(self.message_cache) > 10000:
            oldest_key = min(self.message_cache.keys())
            del self.message_cache[oldest_key]

    async def on_message_edited(self, event):
        """Mesaj düzenlendiğinde"""
        msg = event.message
        old_data = self.message_cache.get(msg.id, {})
        old_text = old_data.get('text', '(Bilinmiyor)')

        self.message_cache[msg.id] = {
            'text': msg.message,
            'media': msg.media,
            'sender_id': msg.sender_id,
            'date': msg.date
        }

        if old_text != msg.message:
            try:
                sender = await self.client.get_entity(msg.sender_id)
                user_info = get_user_info(sender)
            except:
                user_info = f"`{msg.sender_id}`"

            log_text = LogFormatter.realtime_message_edited(
                user_info,
                old_text,
                msg.message if msg.message else "İçerik yok",
                format_date(msg.edit_date),
                msg.id
            )
            await self.send_log(log_text)

    async def on_message_deleted(self, event):
        """Mesaj silindiğinde"""
        for msg_id in event.deleted_ids:
            cached = self.message_cache.get(msg_id)
            if cached:
                try:
                    sender = await self.client.get_entity(cached['sender_id'])
                    user_info = get_user_info(sender)
                except:
                    user_info = f"`{cached.get('sender_id', 'Bilinmiyor')}`"

                text = cached.get('text', '')
                media_info = get_media_info(cached.get('media'))
                content_text = get_content_text(text, media_info)

                log_text = LogFormatter.realtime_message_deleted(
                    user_info,
                    content_text,
                    format_date(cached.get('date')),
                    msg_id
                )

                if cached.get('media'):
                    try:
                        file = await self.client.download_media(cached['media'], bytes)
                        await self.send_log(log_text, file=file)
                    except:
                        await self.send_log(log_text)
                else:
                    await self.send_log(log_text)

                del self.message_cache[msg_id]

    async def on_chat_action(self, event):
        """Üye giriş/çıkış"""
        if event.user_joined or event.user_added:
            try:
                user = await event.get_user()
                user_info = get_user_info(user)
            except:
                user_info = "Bilinmiyor"

            if event.user_added:
                try:
                    added_by = await event.get_added_by()
                    added_by_info = get_user_info(added_by)
                except:
                    added_by_info = "Bilinmiyor"

                log_text = LogFormatter.member_added(
                    user_info,
                    added_by_info,
                    format_date(datetime.now())
                )
            else:
                log_text = LogFormatter.member_joined(
                    user_info,
                    format_date(datetime.now())
                )
            await self.send_log(log_text)

        elif event.user_left or event.user_kicked:
            try:
                user = await event.get_user()
                user_info = get_user_info(user)
            except:
                user_info = "Bilinmiyor"

            if event.user_kicked:
                log_text = LogFormatter.member_kicked(
                    user_info,
                    format_date(datetime.now())
                )
            else:
                log_text = LogFormatter.member_left(
                    user_info,
                    format_date(datetime.now())
                )
            await self.send_log(log_text)

    async def check_admin_log(self):
        """Admin log'u periyodik kontrol et"""
        while True:
            try:
                result = await self.client(GetAdminLogRequest(
                    channel=self.config.source_group_id,
                    q='',
                    min_id=self.last_event_id,
                    max_id=0,
                    limit=100,
                    events_filter=None,
                    admins=None
                ))

                users_dict = {u.id: u for u in result.users}
                events_list = sorted(result.events, key=lambda x: x.id)

                for event in events_list:
                    if event.id > self.last_event_id:
                        await self.action_processor.process(event, users_dict)
                        self.last_event_id = event.id

            except Exception as e:
                logger.error(f"Admin log hatası: {e}")

            await asyncio.sleep(self.config.check_interval)
