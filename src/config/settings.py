"""
Harley Telegram Bot - Konfigürasyon Ayarları
=============================================
Tüm bot ayarları tek bir yerden yönetilir
"""

import os
from dataclasses import dataclass, field
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()


def parse_int_list(value: str) -> List[int]:
    """Virgülle ayrılmış string'i int listesine çevir"""
    if not value:
        return []
    return [int(x.strip()) for x in value.split(",") if x.strip()]


@dataclass
class TelegramConfig:
    """Telegram API ayarları"""
    api_id: int
    api_hash: str
    session_string: str

    @classmethod
    def from_env(cls) -> "TelegramConfig":
        return cls(
            api_id=int(os.getenv("API_ID", "0")),
            api_hash=os.getenv("API_HASH", ""),
            session_string=os.getenv("SESSION_STRING", "")
        )


@dataclass
class LogBotConfig:
    """Log Bot modülü ayarları"""
    enabled: bool
    source_group_id: int
    log_group_id: int
    check_interval: int = 5  # saniye

    @classmethod
    def from_env(cls) -> "LogBotConfig":
        source = int(os.getenv("LOG_SOURCE_GROUP_ID", "0"))
        log = int(os.getenv("LOG_TARGET_GROUP_ID", "0"))
        return cls(
            enabled=bool(source and log),
            source_group_id=source,
            log_group_id=log,
            check_interval=int(os.getenv("LOG_CHECK_INTERVAL", "5"))
        )


@dataclass
class GroupSet:
    """Bir grup seti tanımı"""
    protected_groups: List[int]
    log_channel_id: int


@dataclass
class AntiSpamConfig:
    """Anti-Spam modülü ayarları"""
    enabled: bool
    group_sets: List[GroupSet] = field(default_factory=list)
    auto_clean_threshold: int = 20
    check_interval: int = 10  # saniye

    @classmethod
    def from_env(cls) -> "AntiSpamConfig":
        group_sets = []

        # Grup Seti 1
        groups_1 = parse_int_list(os.getenv("PROTECTED_GROUPS_1", ""))
        log_1 = int(os.getenv("LOG_CHANNEL_ID_1", "0"))
        if groups_1 and log_1:
            group_sets.append(GroupSet(protected_groups=groups_1, log_channel_id=log_1))

        # Grup Seti 2
        groups_2 = parse_int_list(os.getenv("PROTECTED_GROUPS_2", ""))
        log_2 = int(os.getenv("LOG_CHANNEL_ID_2", "0"))
        if groups_2 and log_2:
            group_sets.append(GroupSet(protected_groups=groups_2, log_channel_id=log_2))

        # Tek grup desteği (eski format)
        single_groups = parse_int_list(os.getenv("PROTECTED_GROUPS", ""))
        single_log = int(os.getenv("LOG_CHANNEL_ID", "0"))
        if single_groups and single_log and not group_sets:
            group_sets.append(GroupSet(protected_groups=single_groups, log_channel_id=single_log))

        return cls(
            enabled=bool(group_sets),
            group_sets=group_sets,
            auto_clean_threshold=int(os.getenv("AUTO_CLEAN_THRESHOLD", "20")),
            check_interval=int(os.getenv("SPAM_CHECK_INTERVAL", "10"))
        )


@dataclass
class Config:
    """Ana konfigürasyon sınıfı"""
    telegram: TelegramConfig
    log_bot: LogBotConfig
    anti_spam: AntiSpamConfig
    debug: bool = False

    @classmethod
    def load(cls) -> "Config":
        """Ortam değişkenlerinden konfigürasyon yükle"""
        return cls(
            telegram=TelegramConfig.from_env(),
            log_bot=LogBotConfig.from_env(),
            anti_spam=AntiSpamConfig.from_env(),
            debug=os.getenv("DEBUG", "").lower() in ("true", "1", "yes")
        )

    def validate(self) -> List[str]:
        """Konfigürasyonu doğrula, hata mesajları döndür"""
        errors = []

        if not self.telegram.api_id:
            errors.append("API_ID ayarlanmamış!")
        if not self.telegram.api_hash:
            errors.append("API_HASH ayarlanmamış!")
        if not self.telegram.session_string:
            errors.append("SESSION_STRING ayarlanmamış!")

        if not self.log_bot.enabled and not self.anti_spam.enabled:
            errors.append("En az bir modül (Log Bot veya Anti-Spam) yapılandırılmalı!")

        return errors

    def print_summary(self):
        """Konfigürasyon özetini yazdır"""
        print("=" * 60)
        print("📋 KONFİGÜRASYON ÖZETİ")
        print("=" * 60)

        print("\n🔐 Telegram API:")
        print(f"   API ID: {'✅ Ayarlı' if self.telegram.api_id else '❌ Eksik'}")
        print(f"   API Hash: {'✅ Ayarlı' if self.telegram.api_hash else '❌ Eksik'}")
        print(f"   Session: {'✅ Ayarlı' if self.telegram.session_string else '❌ Eksik'}")

        print("\n📝 Log Bot Modülü:")
        if self.log_bot.enabled:
            print(f"   ✅ Aktif")
            print(f"   Kaynak Grup: {self.log_bot.source_group_id}")
            print(f"   Log Grubu: {self.log_bot.log_group_id}")
            print(f"   Kontrol Aralığı: {self.log_bot.check_interval}sn")
        else:
            print("   ⚪ Devre Dışı")

        print("\n🛡️ Anti-Spam Modülü:")
        if self.anti_spam.enabled:
            print(f"   ✅ Aktif")
            print(f"   Otomatik Temizleme Eşiği: {self.anti_spam.auto_clean_threshold}")
            print(f"   Kontrol Aralığı: {self.anti_spam.check_interval}sn")
            for i, gs in enumerate(self.anti_spam.group_sets, 1):
                print(f"   Grup Seti {i}: {len(gs.protected_groups)} grup, Log: {gs.log_channel_id}")
        else:
            print("   ⚪ Devre Dışı")

        print("\n" + "=" * 60)
