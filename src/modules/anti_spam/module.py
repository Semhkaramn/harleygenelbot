"""
Harley Telegram Bot - Anti-Spam Modülü
=======================================
Katılım isteklerini otomatik temizler
"""

import asyncio
import logging
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from telethon import events
from telethon.tl.functions.messages import HideChatJoinRequestRequest, GetChatInviteImportersRequest
from telethon.tl.types import InputUserEmpty

from ...core.events import ModuleState

logger = logging.getLogger(__name__)


@dataclass
class GroupStats:
    """Grup bazlı istatistikler"""
    pending_count: int = 0


@dataclass
class GroupSetStats:
    """Bir grup seti için istatistikler"""
    total_rejected: int = 0
    groups: Dict[int, GroupStats] = field(default_factory=dict)
    state: ModuleState = ModuleState.ACTIVE
    clearing_in_progress: bool = False
    accumulated_rejected: int = 0
    last_cleanup_time: Optional[datetime] = None


class AntiSpamModule:
    """Anti-Spam Modülü"""

    def __init__(self, bot, config):
        self.bot = bot
        self.config = config
        self.client = bot.client

        # Her grup seti için ayrı state
        self.group_sets: Dict[int, dict] = {}
        self.log_to_set: Dict[int, int] = {}

        # Grup setlerini yükle
        for i, gs in enumerate(config.group_sets, 1):
            self.group_sets[i] = {
                'protected_groups': gs.protected_groups,
                'log_channel': gs.log_channel_id,
                'stats': GroupSetStats()
            }
            self.log_to_set[gs.log_channel_id] = i
            logger.info(f"Grup Seti {i}: {len(gs.protected_groups)} grup, Log: {gs.log_channel_id}")

    async def start(self):
        """Modülü başlat"""
        logger.info("Anti-Spam modülü başlatılıyor...")

        # Komut handler'ı ekle
        all_log_channels = [data['log_channel'] for data in self.group_sets.values()]

        if all_log_channels:
            self.client.add_event_handler(
                self.on_command,
                events.NewMessage(
                    chats=all_log_channels,
                    pattern=r'^/(ac|kapat|temizle)$'
                )
            )

        # Başlangıçta kontrol et
        for set_id in self.group_sets:
            await self.check_and_auto_clean(set_id)

        # Periyodik kontrol başlat
        self.bot.add_task(self.periodic_check())

        logger.info("Anti-Spam modülü başlatıldı")

    async def periodic_check(self):
        """Periyodik istek kontrolü"""
        logger.info(f"Periyodik kontrol başlatıldı ({self.config.check_interval}sn aralık)")
        check_count = 0

        while True:
            await asyncio.sleep(self.config.check_interval)
            check_count += 1

            for set_id, data in self.group_sets.items():
                stats = data['stats']

                if stats.state != ModuleState.ACTIVE:
                    continue

                if stats.clearing_in_progress:
                    continue

                # 2 dakika silme olmadıysa log at
                if stats.last_cleanup_time and stats.accumulated_rejected > 0:
                    elapsed = (datetime.now() - stats.last_cleanup_time).total_seconds()
                    if elapsed >= 120:
                        await self.send_log(set_id, f"✅ {stats.accumulated_rejected} istek temizlendi")
                        stats.accumulated_rejected = 0
                        stats.last_cleanup_time = None

                # Toplam bekleyen sayısı
                total_pending = 0
                for group_id in data['protected_groups']:
                    count = await self.get_pending_count(group_id)
                    total_pending += count

                if check_count % 3 == 0:
                    logger.info(f"[Periyodik] Set {set_id} - Bekleyen: {total_pending}, Eşik: {self.config.auto_clean_threshold}")

                if total_pending > self.config.auto_clean_threshold:
                    logger.info(f"[Periyodik] Set {set_id} - Eşik aşıldı! Temizleme başlatılıyor...")
                    await self.do_cleanup(set_id, manual=False)

    async def on_command(self, event):
        """Komut handler"""
        command = event.text.lower().strip('/')
        chat_id = event.chat_id

        set_id = self.log_to_set.get(chat_id)
        if set_id is None:
            return

        data = self.group_sets[set_id]
        stats = data['stats']

        if command == 'ac':
            if stats.state == ModuleState.ACTIVE:
                await event.reply(f"Bot zaten aktif! (Set {set_id})")
                return
            if stats.state == ModuleState.CLEARING:
                await event.reply("Temizleme devam ediyor...")
                return

            stats.state = ModuleState.ACTIVE
            logger.info(f"Set {set_id} AKTİF edildi")
            await event.reply(f"🟢 Bot aktif! (Set {set_id})")
            await self.check_and_auto_clean(set_id)

        elif command == 'kapat':
            if stats.state == ModuleState.INACTIVE:
                await event.reply(f"Bot zaten kapalı! (Set {set_id})")
                return
            if stats.state == ModuleState.CLEARING:
                await event.reply("Temizleme devam ediyor...")
                return

            stats.state = ModuleState.INACTIVE
            logger.info(f"Set {set_id} KAPATILDI")
            await event.reply(f"🔴 Bot kapatıldı! (Set {set_id})")

        elif command == 'temizle':
            if stats.clearing_in_progress:
                await event.reply("Temizleme zaten devam ediyor...")
                return
            await self.do_cleanup(set_id, manual=True)

    async def do_cleanup(self, set_id: int, manual=False):
        """Grup setindeki istekleri temizle"""
        data = self.group_sets[set_id]
        stats = data['stats']

        if stats.clearing_in_progress:
            return

        logger.info(f"Set {set_id} - Temizleme başlıyor (Manual: {manual})")

        previous_state = stats.state
        stats.state = ModuleState.CLEARING
        stats.clearing_in_progress = True

        total_rejected = 0
        for group_id in data['protected_groups']:
            rejected = await self.clear_all_requests(group_id)
            total_rejected += rejected
            logger.info(f"Grup {group_id} - {rejected} istek reddedildi")

        stats.clearing_in_progress = False
        stats.state = previous_state if not manual else ModuleState.INACTIVE

        stats.accumulated_rejected += total_rejected
        stats.last_cleanup_time = datetime.now()

        logger.info(f"Set {set_id} - Temizleme tamamlandı: {total_rejected} istek")

        if total_rejected > 0:
            await self.send_log(set_id, f"🗑️ {total_rejected} istek silindi (Otomatik: {not manual})")

    async def clear_all_requests(self, chat_id: int) -> int:
        """Bir gruptaki tüm istekleri reddet"""
        total_rejected = 0

        try:
            while True:
                try:
                    result = await self.client(GetChatInviteImportersRequest(
                        peer=chat_id,
                        requested=True,
                        limit=100,
                        offset_date=None,
                        offset_user=InputUserEmpty(),
                        q=""
                    ))

                    if not result.importers:
                        break

                    for importer in result.importers:
                        try:
                            await self.client(HideChatJoinRequestRequest(
                                peer=chat_id,
                                user_id=importer.user_id,
                                approved=False
                            ))
                            total_rejected += 1

                            if total_rejected % 10 == 0:
                                logger.info(f"{total_rejected} istek reddedildi...")

                            await asyncio.sleep(0.03)
                        except Exception as e:
                            if "HIDE_REQUESTER_MISSING" in str(e):
                                continue
                            logger.error(f"Red hatası: {e}")
                            await asyncio.sleep(0.1)

                except Exception as e:
                    error_str = str(e)
                    if "FLOOD_WAIT" in error_str:
                        import re
                        wait_match = re.search(r'(\d+)', error_str)
                        wait_time = int(wait_match.group(1)) if wait_match else 5
                        logger.warning(f"FloodWait: {wait_time}sn bekleniyor...")
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        logger.error(f"İstek listesi hatası: {e}")
                        break

                await asyncio.sleep(0.5)

        except Exception as e:
            logger.error(f"Grup erişim hatası {chat_id}: {e}")

        return total_rejected

    async def get_pending_count(self, chat_id: int) -> int:
        """Bekleyen istek sayısını al"""
        try:
            result = await self.client(GetChatInviteImportersRequest(
                peer=chat_id,
                requested=True,
                limit=1,
                offset_date=None,
                offset_user=InputUserEmpty(),
                q=""
            ))
            return result.count if hasattr(result, 'count') else len(result.importers)
        except Exception as e:
            logger.error(f"Bekleyen istek sayısı alınamadı ({chat_id}): {e}")
            return 0

    async def check_and_auto_clean(self, set_id: int):
        """Eşik kontrolü ve otomatik temizleme"""
        data = self.group_sets[set_id]
        stats = data['stats']

        if stats.state != ModuleState.ACTIVE:
            return

        if stats.clearing_in_progress:
            return

        total_pending = 0
        for group_id in data['protected_groups']:
            count = await self.get_pending_count(group_id)
            total_pending += count

        logger.info(f"Set {set_id} - Bekleyen: {total_pending}, Eşik: {self.config.auto_clean_threshold}")

        if total_pending > self.config.auto_clean_threshold:
            await self.do_cleanup(set_id, manual=False)

    async def send_log(self, set_id: int, message: str):
        """Log mesajı gönder"""
        data = self.group_sets.get(set_id)
        if not data:
            return

        log_channel = data['log_channel']
        if not log_channel:
            return

        try:
            await self.client.send_message(log_channel, f"[Set {set_id}] {message}")
        except Exception as e:
            logger.error(f"Log gönderme hatası: {e}")
