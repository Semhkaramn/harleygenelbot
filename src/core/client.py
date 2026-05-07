"""
Harley Telegram Bot - Client Yöneticisi
========================================
Telegram client bağlantı ve oturum yönetimi
"""

import asyncio
import logging
from typing import Optional, List, Callable, Any

from telethon import TelegramClient
from telethon.sessions import StringSession

from ..config import Config
from .events import BotState

logger = logging.getLogger(__name__)


class TelegramBot:
    """Telegram Bot ana sınıfı"""

    def __init__(self, config: Config):
        self.config = config
        self.client: Optional[TelegramClient] = None
        self.state = BotState.STOPPED
        self.me = None
        self._modules: List[Any] = []
        self._tasks: List[asyncio.Task] = []

    async def connect(self) -> bool:
        """Telegram'a bağlan"""
        try:
            self.state = BotState.STARTING
            logger.info("Telegram'a bağlanılıyor...")

            self.client = TelegramClient(
                StringSession(self.config.telegram.session_string),
                self.config.telegram.api_id,
                self.config.telegram.api_hash
            )

            await self.client.connect()

            if not await self.client.is_user_authorized():
                logger.error("Session geçersiz veya süresi dolmuş!")
                self.state = BotState.ERROR
                return False

            self.me = await self.client.get_me()
            logger.info(f"Giriş başarılı: {self.me.first_name} (@{self.me.username})")

            self.state = BotState.RUNNING
            return True

        except Exception as e:
            logger.error(f"Bağlantı hatası: {e}")
            self.state = BotState.ERROR
            return False

    async def disconnect(self):
        """Bağlantıyı kapat"""
        self.state = BotState.STOPPING
        logger.info("Bot kapatılıyor...")

        # Görevleri iptal et
        for task in self._tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

        # Client'ı kapat
        if self.client:
            await self.client.disconnect()

        self.state = BotState.STOPPED
        logger.info("Bot kapatıldı")

    def register_module(self, module: Any):
        """Modül kaydet"""
        self._modules.append(module)
        logger.info(f"Modül kaydedildi: {module.__class__.__name__}")

    def add_task(self, coro: Callable):
        """Arka plan görevi ekle"""
        task = asyncio.create_task(coro)
        self._tasks.append(task)
        return task

    async def get_entity(self, entity_id: int):
        """Entity bilgisi al"""
        try:
            return await self.client.get_entity(entity_id)
        except Exception as e:
            logger.error(f"Entity alınamadı ({entity_id}): {e}")
            return None

    async def send_message(self, chat_id: int, text: str, **kwargs):
        """Mesaj gönder"""
        try:
            return await self.client.send_message(
                chat_id,
                text,
                parse_mode='md',
                link_preview=False,
                **kwargs
            )
        except Exception as e:
            logger.error(f"Mesaj gönderilemedi ({chat_id}): {e}")
            return None

    async def run(self):
        """Bot'u çalıştır"""
        if not await self.connect():
            return

        logger.info("Bot çalışıyor...")

        # Modülleri başlat
        for module in self._modules:
            if hasattr(module, 'start'):
                await module.start()

        try:
            await self.client.run_until_disconnected()
        except KeyboardInterrupt:
            logger.info("Kullanıcı tarafından durduruldu")
        finally:
            await self.disconnect()
