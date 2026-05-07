"""
Harley Telegram Bot - Yardımcı Fonksiyonlar
============================================
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Any

from telethon.tl.types import (
    MessageMediaPhoto,
    MessageMediaDocument,
    MessageMediaWebPage,
    MessageMediaGeo,
    MessageMediaContact,
    MessageMediaPoll,
    MessageMediaDice,
    DocumentAttributeFilename,
    DocumentAttributeVideo,
    DocumentAttributeAudio,
    DocumentAttributeSticker,
    DocumentAttributeAnimated,
)


# Türkiye saat dilimi (UTC+3)
TR_TIMEZONE = timezone(timedelta(hours=3))


def get_user_info(user: Any) -> str:
    """
    Kullanıcı bilgisini formatla

    Args:
        user: Telegram kullanıcı objesi

    Returns:
        Formatlanmış kullanıcı bilgisi string'i
    """
    if not user:
        return "Bilinmiyor"

    # İsim oluştur
    name = ""
    if hasattr(user, 'first_name') and user.first_name:
        name = user.first_name
    if hasattr(user, 'last_name') and user.last_name:
        name += f" {user.last_name}"

    if not name:
        name = "İsimsiz"

    # ID ve username
    user_id = user.id if hasattr(user, 'id') else 0
    username = f"@{user.username}" if hasattr(user, 'username') and user.username else ""

    # Mention formatı
    mention = f"[{name}](tg://user?id={user_id})"

    return f"{mention} {username}\n`ID: {user_id}`"


def format_date(dt: Optional[datetime]) -> str:
    """
    Tarihi TR saatine çevir ve formatla

    Args:
        dt: datetime objesi

    Returns:
        Formatlanmış tarih string'i
    """
    if not dt:
        return "Bilinmiyor"

    # Eğer datetime timezone-aware değilse UTC olarak kabul et
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    # TR saatine çevir
    tr_time = dt.astimezone(TR_TIMEZONE)

    return tr_time.strftime("%d.%m.%Y • %H:%M:%S")


def get_media_info(media: Any) -> Optional[str]:
    """
    Medya bilgisini al

    Args:
        media: Telegram medya objesi

    Returns:
        Medya açıklaması veya None
    """
    if not media:
        return None

    if isinstance(media, MessageMediaPhoto):
        return "Fotoğraf"

    elif isinstance(media, MessageMediaDocument):
        doc = media.document
        if doc:
            for attr in doc.attributes:
                if isinstance(attr, DocumentAttributeSticker):
                    return "Sticker"
                elif isinstance(attr, DocumentAttributeAnimated):
                    return "GIF"
                elif isinstance(attr, DocumentAttributeVideo):
                    if attr.round_message:
                        return f"Video Mesaj ({attr.duration}sn)"
                    return f"Video ({attr.duration}sn, {attr.w}x{attr.h})"
                elif isinstance(attr, DocumentAttributeAudio):
                    if attr.voice:
                        return f"Sesli Mesaj ({attr.duration}sn)"
                    return f"Ses ({attr.duration}sn)"
                elif isinstance(attr, DocumentAttributeFilename):
                    size = doc.size / 1024 / 1024
                    return f"Dosya: {attr.file_name} ({size:.2f}MB)"
            return "Belge"

    elif isinstance(media, MessageMediaWebPage):
        return "Web Önizleme"

    elif isinstance(media, MessageMediaGeo):
        return "Konum"

    elif isinstance(media, MessageMediaContact):
        return "Kişi"

    elif isinstance(media, MessageMediaPoll):
        return "Anket"

    elif isinstance(media, MessageMediaDice):
        return f"Zar: {media.value}"

    return "Medya"


def truncate_text(text: str, max_length: int = 500) -> str:
    """
    Metni belirli uzunlukta kes

    Args:
        text: Kesilecek metin
        max_length: Maksimum uzunluk

    Returns:
        Kesilmiş metin
    """
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def escape_markdown(text: str) -> str:
    """
    Markdown özel karakterlerini escape et

    Args:
        text: Escape edilecek metin

    Returns:
        Escape edilmiş metin
    """
    if not text:
        return ""

    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text


def get_content_text(text: str, media_info: Optional[str]) -> str:
    """
    İçerik metnini oluştur (metin + medya bilgisi)

    Args:
        text: Mesaj metni
        media_info: Medya bilgisi

    Returns:
        Birleştirilmiş içerik metni
    """
    if text and media_info:
        return f"{text}\n┃ ╰ 📎 {media_info}"
    elif text:
        return text
    elif media_info:
        return f"📎 {media_info}"
    else:
        return "⚠️ İçerik bulunamadı"
