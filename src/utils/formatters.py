"""
Harley Telegram Bot - Formatlayıcılar
======================================
Haklar, süre ve diğer verilerin formatlanması
"""

from typing import Optional
from telethon.tl.types import ChatBannedRights, ChatAdminRights


def format_banned_rights(rights: Optional[ChatBannedRights]) -> str:
    """
    Yasak haklarını formatla

    Args:
        rights: ChatBannedRights objesi

    Returns:
        Formatlanmış yasak hakları listesi
    """
    if not rights:
        return "Yok"

    bans = []

    if rights.view_messages:
        bans.append("Mesaj Görme")
    if rights.send_messages:
        bans.append("Mesaj Gönderme")
    if rights.send_media:
        bans.append("Medya Gönderme")
    if rights.send_stickers:
        bans.append("Sticker")
    if rights.send_gifs:
        bans.append("GIF")
    if rights.send_games:
        bans.append("Oyun")
    if rights.send_inline:
        bans.append("Inline Bot")
    if rights.embed_links:
        bans.append("Link Önizleme")
    if rights.send_polls:
        bans.append("Anket")
    if rights.change_info:
        bans.append("Bilgi Değiştirme")
    if rights.invite_users:
        bans.append("Davet Etme")
    if rights.pin_messages:
        bans.append("Sabitleme")

    if not bans:
        return "Kısıtlama Yok"

    return ", ".join(bans)


def format_admin_rights(rights: Optional[ChatAdminRights]) -> str:
    """
    Admin haklarını formatla

    Args:
        rights: ChatAdminRights objesi

    Returns:
        Formatlanmış admin hakları listesi
    """
    if not rights:
        return "Yok"

    perms = []

    if rights.change_info:
        perms.append("Bilgi Değiştir")
    if rights.post_messages:
        perms.append("Mesaj Gönder")
    if rights.edit_messages:
        perms.append("Mesaj Düzenle")
    if rights.delete_messages:
        perms.append("Mesaj Sil")
    if rights.ban_users:
        perms.append("Yasakla")
    if rights.invite_users:
        perms.append("Davet Et")
    if rights.pin_messages:
        perms.append("Sabitle")
    if rights.add_admins:
        perms.append("Admin Ekle")
    if rights.anonymous:
        perms.append("Anonim")
    if rights.manage_call:
        perms.append("Görüşme Yönet")
    if rights.other:
        perms.append("Diğer")

    if not perms:
        return "Yetki Yok"

    return ", ".join(perms)


def format_ttl(seconds: int) -> str:
    """
    Otomatik silme süresini formatla

    Args:
        seconds: Saniye cinsinden süre

    Returns:
        Formatlanmış süre string'i
    """
    if seconds == 0:
        return "Kapalı"
    elif seconds < 60:
        return f"{seconds} saniye"
    elif seconds < 3600:
        return f"{seconds // 60} dakika"
    elif seconds < 86400:
        return f"{seconds // 3600} saat"
    else:
        return f"{seconds // 86400} gün"


def format_slow_mode(seconds: int) -> str:
    """
    Yavaş mod süresini formatla

    Args:
        seconds: Saniye cinsinden süre

    Returns:
        Formatlanmış süre string'i
    """
    if seconds == 0:
        return "Kapalı"
    elif seconds < 60:
        return f"{seconds} saniye"
    elif seconds < 3600:
        return f"{seconds // 60} dakika"
    else:
        return f"{seconds // 3600} saat"


def format_volume(volume: int) -> str:
    """
    Ses seviyesini formatla

    Args:
        volume: Ses seviyesi (0-10000)

    Returns:
        Formatlanmış yüzde string'i
    """
    return f"%{volume // 100}"


def format_file_size(size_bytes: int) -> str:
    """
    Dosya boyutunu formatla

    Args:
        size_bytes: Byte cinsinden boyut

    Returns:
        Formatlanmış boyut string'i
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"
