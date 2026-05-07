#!/usr/bin/env python3
"""
HARLEY TELEGRAM BOT
===================
Log Bot + Anti-Spam birleşik bot
"""

import asyncio
import logging
import sys

from src.config import Config
from src.core.client import TelegramBot
from src.modules.log_bot import LogBotModule
from src.modules.anti_spam import AntiSpamModule

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)


async def main():
    """Ana fonksiyon"""
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                 HARLEY TELEGRAM BOT                       ║
    ╠═══════════════════════════════════════════════════════════╣
    ║  📝 Log Bot: Admin log'ları izler                        ║
    ║  🛡️ Anti-Spam: Katılım isteklerini yönetir               ║
    ║                                                           ║
    ║  Komutlar: /ac  /kapat  /temizle                         ║
    ╚═══════════════════════════════════════════════════════════╝
    """)

    config = Config.load()
    config.print_summary()

    errors = config.validate()
    if errors:
        for error in errors:
            logger.error(f"Konfigürasyon hatası: {error}")
        return

    bot = TelegramBot(config)

    if not await bot.connect():
        logger.error("Telegram'a bağlanılamadı!")
        return

    modules_loaded = 0

    if config.log_bot.enabled:
        try:
            log_module = LogBotModule(bot, config.log_bot)
            bot.register_module(log_module)
            modules_loaded += 1
            logger.info("Log Bot modülü yüklendi")
        except Exception as e:
            logger.error(f"Log Bot modülü yüklenemedi: {e}")

    if config.anti_spam.enabled:
        try:
            spam_module = AntiSpamModule(bot, config.anti_spam)
            bot.register_module(spam_module)
            modules_loaded += 1
            logger.info("Anti-Spam modülü yüklendi")
        except Exception as e:
            logger.error(f"Anti-Spam modülü yüklenemedi: {e}")

    if modules_loaded == 0:
        logger.error("Hiçbir modül yüklenemedi!")
        return

    logger.info(f"{modules_loaded} modül yüklendi. Bot çalışıyor...")
    await bot.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Bot durduruldu!")
