"""
Harley Telegram Bot - Log Formatters
=====================================
Log mesajları için şablon formatları
"""

from typing import Optional, Dict, Any
from datetime import datetime

from ...utils.helpers import (
    get_user_info,
    format_date,
    get_media_info,
    get_content_text
)
from ...utils.formatters import (
    format_banned_rights,
    format_admin_rights,
    format_ttl,
    format_slow_mode,
    format_volume
)


class LogFormatter:
    """Log mesajı formatlayıcısı"""

    @staticmethod
    def message_deleted(
        user_info: str,
        msg_sender_info: str,
        content_text: str,
        msg_date: str,
        date: str,
        msg_id: int
    ) -> str:
        """Mesaj silindi log formatı"""
        return f"""#Mesaj_Silindi
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
┃ 🗑 **MESAJ SİLİNDİ**
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
┃
┃ 👮 **SİLEN YETKİLİ:**
┃ ╰ {user_info}
┃
┃ 👤 **MESAJ SAHİBİ:**
┃ ╰ {msg_sender_info}
┃
┃ 📝 **SİLİNEN İÇERİK:**
┃ ╰ {content_text}
┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
┃ 📅 Gönderim: `{msg_date}`
┃ 🗑 Silinme: `{date}`
┃ 🆔 Mesaj ID: `{msg_id}`
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""

    @staticmethod
    def message_edited(
        user_info: str,
        old_text: str,
        new_text: str,
        date: str,
        msg_id: int
    ) -> str:
        """Mesaj düzenlendi log formatı"""
        return f"""#Mesaj_Düzenlendi
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
┃ ✏️ **MESAJ DÜZENLENDİ**
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
┃
┃ 👤 **DÜZENLEYEN:**
┃ ╰ {user_info}
┃
┃ 📝 **ESKİ İÇERİK:**
┃ ╰ {old_text}
┃
┃ 📝 **YENİ İÇERİK:**
┃ ╰ {new_text}
┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
┃ 📅 Düzenleme: `{date}`
┃ 🆔 Mesaj ID: `{msg_id}`
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""

    @staticmethod
    def message_pinned(
        user_info: str,
        msg_sender_info: str,
        content_text: str,
        date: str,
        msg_id: Optional[int],
        is_pinned: bool = True
    ) -> str:
        """Mesaj sabitleme/kaldırma log formatı"""
        tag = "#Mesaj_Sabitlendi" if is_pinned else "#Sabit_Kaldırıldı"
        emoji = "📌" if is_pinned else "📍"
        action = "SABİTLENDİ" if is_pinned else "SABİT KALDIRILDI"

        msg_id_line = f"┃ 🆔 Mesaj ID: `{msg_id}`\n" if msg_id else ""

        return f"""{tag}
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
┃ {emoji} **MESAJ {action}**
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
┃
┃ 👮 **İŞLEMİ YAPAN:**
┃ ╰ {user_info}
┃
┃ 👤 **MESAJ SAHİBİ:**
┃ ╰ {msg_sender_info}
┃
┃ 📝 **MESAJ İÇERİĞİ:**
┃ ╰ {content_text}
┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
┃ 📅 İşlem: `{date}`
{msg_id_line}┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""

    @staticmethod
    def member_joined(user_info: str, date: str) -> str:
        """Üye katıldı log formatı"""
        return f"""#Gruba_Katıldı
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
┃ 📥 **YENİ ÜYE KATILDI**
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
┃
┃ 👤 **KATILAN ÜYE:**
┃ ╰ {user_info}
┃
┃ 🔗 **KATILIM ŞEKLİ:**
┃ ╰ Direkt Katılım (Link ile)
┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
┃ 📅 Katılım: `{date}`
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""

    @staticmethod
    def member_left(user_info: str, date: str) -> str:
        """Üye ayrıldı log formatı"""
        return f"""#Gruptan_Ayrıldı
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
┃ 📤 **ÜYE GRUPTAN AYRILDI**
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
┃
┃ 👤 **AYRILAN ÜYE:**
┃ ╰ {user_info}
┃
┃ 🚶 **AYRILMA ŞEKLİ:**
┃ ╰ Kendi İsteğiyle Ayrıldı
┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
┃ 📅 Ayrılma: `{date}`
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""

    @staticmethod
    def member_invited(
        user_info: str,
        invited_info: str,
        date: str
    ) -> str:
        """Üye davet edildi log formatı"""
        return f"""#Üye_Davet_Edildi
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
┃ 📨 **ÜYE DAVET EDİLDİ**
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
┃
┃ 👮 **DAVET EDEN:**
┃ ╰ {user_info}
┃
┃ 👤 **DAVET EDİLEN:**
┃ ╰ {invited_info}
┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
┃ 📅 Davet: `{date}`
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""

    @staticmethod
    def member_banned(
        user_info: str,
        target_info: str,
        old_restrictions: str,
        new_restrictions: str,
        until_text: str,
        date: str,
        action_type: str  # 'ban', 'unban', 'restrict', 'unrestrict'
    ) -> str:
        """Ban/kısıtlama log formatı"""

        if action_type == 'ban':
            tag = "#Üye_Yasaklandı"
            emoji = "🚫"
            action = "ÜYE YASAKLANDI (BAN)"
        elif action_type == 'unban':
            tag = "#Yasak_Kaldırıldı"
            emoji = "✅"
            action = "YASAK KALDIRILDI (UNBAN)"
        elif action_type == 'restrict':
            tag = "#Üye_Kısıtlandı"
            emoji = "🔒"
            action = "ÜYE KISITLANDI"
        else:
            tag = "#Kısıtlama_Kaldırıldı"
            emoji = "🔓"
            action = "KISITLAMA KALDIRILDI"

        until_line = f"\n┃ ⏰ **BİTİŞ TARİHİ:**\n┃ ╰ `{until_text}`\n┃" if until_text else ""

        return f"""{tag}
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
┃ {emoji} **{action}**
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
┃
┃ 👮 **İŞLEMİ YAPAN YETKİLİ:**
┃ ╰ {user_info}
┃
┃ 👤 **HEDEF ÜYE:**
┃ ╰ {target_info}
┃
┃ 📋 **ÖNCEKİ KISITLAMALAR:**
┃ ╰ {old_restrictions}
┃
┃ 📋 **YENİ KISITLAMALAR:**
┃ ╰ {new_restrictions}
┃{until_line}
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
┃ 📅 İşlem: `{date}`
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""

    @staticmethod
    def admin_changed(
        user_info: str,
        target_info: str,
        old_perms: str,
        new_perms: str,
        rank: Optional[str],
        date: str,
        action_type: str  # 'promote', 'demote', 'change'
    ) -> str:
        """Admin değişikliği log formatı"""

        if action_type == 'promote':
            tag = "#Admin_Yapıldı"
            emoji = "👑"
            action = "YENİ ADMİN ATANDI"
        elif action_type == 'demote':
            tag = "#Adminlik_Alındı"
            emoji = "👤"
            action = "ADMİNLİK ALINDI"
        else:
            tag = "#Admin_Yetkileri_Değişti"
            emoji = "⚙️"
            action = "ADMİN YETKİLERİ DEĞİŞTİ"

        rank_line = f"\n┃ 🏷 **ÜNVAN:**\n┃ ╰ `{rank}`\n┃" if rank else ""

        return f"""{tag}
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
┃ {emoji} **{action}**
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
┃
┃ 👮 **İŞLEMİ YAPAN:**
┃ ╰ {user_info}
┃
┃ 👤 **HEDEF ÜYE:**
┃ ╰ {target_info}
┃{rank_line}
┃ 📋 **ÖNCEKİ YETKİLER:**
┃ ╰ {old_perms}
┃
┃ 📋 **YENİ YETKİLER:**
┃ ╰ {new_perms}
┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
┃ 📅 İşlem: `{date}`
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""

    @staticmethod
    def simple_log(
        tag: str,
        emoji: str,
        title: str,
        user_info: str,
        date: str,
        **extra_fields
    ) -> str:
        """Basit log formatı (genel amaçlı)"""
        extra_lines = ""
        for key, value in extra_fields.items():
            if value:
                extra_lines += f"\n◈ **{key}:** {value}"

        return f"""{tag}

{emoji} **{title}**

◈ **İşlemi Yapan:** {user_info}{extra_lines}
◈ **İşlem Tarihi:** `{date}`"""

    @staticmethod
    def realtime_message_deleted(
        user_info: str,
        content_text: str,
        send_date: str,
        msg_id: int
    ) -> str:
        """Gerçek zamanlı mesaj silindi log formatı"""
        return f"""#Mesaj_Silindi_Gerçek_Zamanlı
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
┃ 🗑️ **MESAJ SİLİNDİ** ⚡
┃ ╰ (Gerçek Zamanlı Tespit)
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
┃
┃ 👤 **MESAJ SAHİBİ:**
┃ ╰ {user_info}
┃
┃ 📝 **SİLİNEN İÇERİK:**
┃ ╰ {content_text}
┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
┃ 📅 Gönderim: `{send_date}`
┃ 🆔 Mesaj ID: `{msg_id}`
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""

    @staticmethod
    def realtime_message_edited(
        user_info: str,
        old_text: str,
        new_text: str,
        edit_date: str,
        msg_id: int
    ) -> str:
        """Gerçek zamanlı mesaj düzenlendi log formatı"""
        return f"""#Mesaj_Düzenlendi_Gerçek_Zamanlı
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
┃ ✏️ **MESAJ DÜZENLENDİ** ⚡
┃ ╰ (Gerçek Zamanlı Tespit)
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
┃
┃ 👤 **DÜZENLEYEN:**
┃ ╰ {user_info}
┃
┃ 📝 **ESKİ İÇERİK:**
┃ ╰ {old_text}
┃
┃ 📝 **YENİ İÇERİK:**
┃ ╰ {new_text}
┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
┃ 📅 Düzenleme: `{edit_date}`
┃ 🆔 Mesaj ID: `{msg_id}`
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""

    @staticmethod
    def member_added(
        user_info: str,
        added_by_info: str,
        date: str
    ) -> str:
        """Üye eklendi log formatı"""
        return f"""#Üye_Eklendi
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
┃ 📨 **ÜYE EKLENDİ** ⚡
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
┃
┃ 👤 **EKLENEN ÜYE:**
┃ ╰ {user_info}
┃
┃ 👮 **EKLEYEN YETKİLİ:**
┃ ╰ {added_by_info}
┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
┃ 📅 Ekleme: `{date}`
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""

    @staticmethod
    def member_kicked(user_info: str, date: str) -> str:
        """Üye atıldı log formatı"""
        return f"""#Üye_Atıldı
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
┃ 👢 **ÜYE ATILDI** ⚡
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
┃
┃ 👤 **ATILAN ÜYE:**
┃ ╰ {user_info}
┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
┃ 📅 Atılma: `{date}`
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""

    @staticmethod
    def bot_started(
        group_title: str,
        bot_name: str,
        date: str
    ) -> str:
        """Bot başlatıldı log formatı"""
        return f"""#Bot_Başlatıldı

🤖 **Log Bot Başlatıldı**

◈ **İzlenen Grup:** {group_title}
◈ **Bot Hesabı:** {bot_name}
◈ **Başlatma Tarihi:** `{date}`

✅ Tüm eylemler loglanacak!"""
