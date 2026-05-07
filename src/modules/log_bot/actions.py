"""
Harley Telegram Bot - Admin Log Action İşleyiciler
===================================================
"""

import logging
from typing import Dict, Any

from telethon.tl.types import (
    ChannelAdminLogEventActionChangeTitle,
    ChannelAdminLogEventActionChangeAbout,
    ChannelAdminLogEventActionChangeUsername,
    ChannelAdminLogEventActionChangePhoto,
    ChannelAdminLogEventActionToggleInvites,
    ChannelAdminLogEventActionToggleSignatures,
    ChannelAdminLogEventActionUpdatePinned,
    ChannelAdminLogEventActionEditMessage,
    ChannelAdminLogEventActionDeleteMessage,
    ChannelAdminLogEventActionParticipantJoin,
    ChannelAdminLogEventActionParticipantLeave,
    ChannelAdminLogEventActionParticipantInvite,
    ChannelAdminLogEventActionParticipantToggleBan,
    ChannelAdminLogEventActionParticipantToggleAdmin,
    ChannelAdminLogEventActionChangeStickerSet,
    ChannelAdminLogEventActionTogglePreHistoryHidden,
    ChannelAdminLogEventActionDefaultBannedRights,
    ChannelAdminLogEventActionStopPoll,
    ChannelAdminLogEventActionChangeLinkedChat,
    ChannelAdminLogEventActionChangeLocation,
    ChannelAdminLogEventActionToggleSlowMode,
    ChannelAdminLogEventActionStartGroupCall,
    ChannelAdminLogEventActionDiscardGroupCall,
    ChannelAdminLogEventActionParticipantMute,
    ChannelAdminLogEventActionParticipantUnmute,
    ChannelAdminLogEventActionToggleGroupCallSetting,
    ChannelAdminLogEventActionParticipantJoinByInvite,
    ChannelAdminLogEventActionExportedInviteDelete,
    ChannelAdminLogEventActionExportedInviteRevoke,
    ChannelAdminLogEventActionExportedInviteEdit,
    ChannelAdminLogEventActionParticipantVolume,
    ChannelAdminLogEventActionChangeHistoryTTL,
    ChannelAdminLogEventActionParticipantJoinByRequest,
    ChannelAdminLogEventActionToggleNoForwards,
    ChannelAdminLogEventActionSendMessage,
    ChannelAdminLogEventActionChangeAvailableReactions,
    ChannelAdminLogEventActionChangeUsernames,
    ChannelAdminLogEventActionToggleForum,
    ChannelAdminLogEventActionCreateTopic,
    ChannelAdminLogEventActionEditTopic,
    ChannelAdminLogEventActionDeleteTopic,
    ChannelAdminLogEventActionPinTopic,
)

from ...utils.helpers import get_user_info, format_date, get_media_info, get_content_text
from ...utils.formatters import format_banned_rights, format_admin_rights, format_ttl
from .formatter import LogFormatter

logger = logging.getLogger(__name__)


class AdminLogActionProcessor:
    """Admin log event işleyici"""

    def __init__(self, client, send_log_callback):
        self.client = client
        self.send_log = send_log_callback

    async def process(self, event, users_dict: Dict[int, Any]):
        """Event'i işle"""
        user = users_dict.get(event.user_id)
        user_info = get_user_info(user)
        date = format_date(event.date)
        action = event.action

        # Mesaj Silme
        if isinstance(action, ChannelAdminLogEventActionDeleteMessage):
            await self._handle_delete_message(action, user_info, date, users_dict)

        # Mesaj Düzenleme
        elif isinstance(action, ChannelAdminLogEventActionEditMessage):
            await self._handle_edit_message(action, user_info, date, users_dict)

        # Mesaj Sabitleme
        elif isinstance(action, ChannelAdminLogEventActionUpdatePinned):
            await self._handle_pin_message(action, user_info, date, users_dict)

        # Üye Katıldı
        elif isinstance(action, ChannelAdminLogEventActionParticipantJoin):
            log_text = LogFormatter.member_joined(user_info, date)
            await self.send_log(log_text)

        # Üye Ayrıldı
        elif isinstance(action, ChannelAdminLogEventActionParticipantLeave):
            log_text = LogFormatter.member_left(user_info, date)
            await self.send_log(log_text)

        # Üye Davet Edildi
        elif isinstance(action, ChannelAdminLogEventActionParticipantInvite):
            invited_user = users_dict.get(action.participant.user_id)
            invited_info = get_user_info(invited_user)
            log_text = LogFormatter.member_invited(user_info, invited_info, date)
            await self.send_log(log_text)

        # Link İle Katıldı
        elif isinstance(action, ChannelAdminLogEventActionParticipantJoinByInvite):
            await self._handle_join_by_invite(action, user_info, date, users_dict)

        # İstek İle Katıldı
        elif isinstance(action, ChannelAdminLogEventActionParticipantJoinByRequest):
            log_text = LogFormatter.simple_log(
                "#İstek_İle_Katıldı", "✋", "Katılım İsteği Onaylandı",
                user_info, date, **{"Katılım Şekli": "İstek Onayı"}
            )
            await self.send_log(log_text)

        # Ban/Kısıtlama
        elif isinstance(action, ChannelAdminLogEventActionParticipantToggleBan):
            await self._handle_ban_toggle(action, user_info, date, users_dict)

        # Admin Değişikliği
        elif isinstance(action, ChannelAdminLogEventActionParticipantToggleAdmin):
            await self._handle_admin_toggle(action, user_info, date, users_dict)

        # Grup Adı Değişti
        elif isinstance(action, ChannelAdminLogEventActionChangeTitle):
            log_text = LogFormatter.simple_log(
                "#Grup_Adı_Değişti", "📝", "Grup Adı Değişikliği",
                user_info, date,
                **{"Eski Ad": f"`{action.prev_value}`", "Yeni Ad": f"`{action.new_value}`"}
            )
            await self.send_log(log_text)

        # Grup Açıklaması Değişti
        elif isinstance(action, ChannelAdminLogEventActionChangeAbout):
            log_text = LogFormatter.simple_log(
                "#Grup_Açıklaması_Değişti", "📄", "Grup Açıklaması Değişikliği",
                user_info, date,
                **{
                    "Eski Açıklama": action.prev_value if action.prev_value else "(Boş)",
                    "Yeni Açıklama": action.new_value if action.new_value else "(Boş)"
                }
            )
            await self.send_log(log_text)

        # Username Değişti
        elif isinstance(action, ChannelAdminLogEventActionChangeUsername):
            log_text = LogFormatter.simple_log(
                "#Grup_Username_Değişti", "🔗", "Grup Kullanıcı Adı Değişikliği",
                user_info, date,
                **{
                    "Eski": f"@{action.prev_value}" if action.prev_value else "(Yok)",
                    "Yeni": f"@{action.new_value}" if action.new_value else "(Yok)"
                }
            )
            await self.send_log(log_text)

        # Fotoğraf Değişti
        elif isinstance(action, ChannelAdminLogEventActionChangePhoto):
            await self._handle_photo_change(action, user_info, date)

        # Davet Linki Ayarı
        elif isinstance(action, ChannelAdminLogEventActionToggleInvites):
            status = "Aktif" if action.new_value else "Kapalı"
            emoji = "🔓" if action.new_value else "🔒"
            log_text = LogFormatter.simple_log(
                "#Davet_Linki_Ayarı", emoji, "Davet Linki Ayar Değişikliği",
                user_info, date, **{"Yeni Durum": status}
            )
            await self.send_log(log_text)

        # İmza Ayarı
        elif isinstance(action, ChannelAdminLogEventActionToggleSignatures):
            status = "Aktif" if action.new_value else "Kapalı"
            log_text = LogFormatter.simple_log(
                "#İmza_Ayarı", "✍", "İmza Ayar Değişikliği",
                user_info, date, **{"Yeni Durum": status}
            )
            await self.send_log(log_text)

        # Yavaş Mod
        elif isinstance(action, ChannelAdminLogEventActionToggleSlowMode):
            status = "Kapalı" if action.new_value == 0 else f"{action.new_value}sn"
            log_text = LogFormatter.simple_log(
                "#Yavaş_Mod", "🐢", "Yavaş Mod Ayar Değişikliği",
                user_info, date, **{"Yeni Süre": status}
            )
            await self.send_log(log_text)

        # Geçmiş Gizliliği
        elif isinstance(action, ChannelAdminLogEventActionTogglePreHistoryHidden):
            status = "Gizli" if action.new_value else "Görünür"
            log_text = LogFormatter.simple_log(
                "#Mesaj_Geçmişi_Ayarı", "📜", "Mesaj Geçmişi Ayar Değişikliği",
                user_info, date, **{"Yeni Üyeler İçin Geçmiş": status}
            )
            await self.send_log(log_text)

        # Varsayılan Kısıtlamalar
        elif isinstance(action, ChannelAdminLogEventActionDefaultBannedRights):
            new_rights = format_banned_rights(action.new_banned_rights)
            old_rights = format_banned_rights(action.prev_banned_rights)
            log_text = LogFormatter.simple_log(
                "#Varsayılan_Kısıtlamalar", "🔒", "Varsayılan Kısıtlama Değişikliği",
                user_info, date,
                **{"Önceki": old_rights, "Yeni": new_rights}
            )
            await self.send_log(log_text)

        # Sticker Seti
        elif isinstance(action, ChannelAdminLogEventActionChangeStickerSet):
            log_text = LogFormatter.simple_log(
                "#Sticker_Seti_Değişti", "🎭", "Sticker Seti Değişikliği",
                user_info, date
            )
            await self.send_log(log_text)

        # Anket Durduruldu
        elif isinstance(action, ChannelAdminLogEventActionStopPoll):
            log_text = LogFormatter.simple_log(
                "#Anket_Durduruldu", "📊", "Anket Durdurma İşlemi",
                user_info, date, **{"Mesaj ID": f"`{action.message.id}`"}
            )
            await self.send_log(log_text)

        # Bağlı Sohbet Değişti
        elif isinstance(action, ChannelAdminLogEventActionChangeLinkedChat):
            log_text = LogFormatter.simple_log(
                "#Bağlı_Sohbet_Değişti", "🔗", "Bağlı Sohbet Değişikliği",
                user_info, date,
                **{"Önceki ID": f"`{action.prev_value}`", "Yeni ID": f"`{action.new_value}`"}
            )
            await self.send_log(log_text)

        # Konum Değişti
        elif isinstance(action, ChannelAdminLogEventActionChangeLocation):
            log_text = LogFormatter.simple_log(
                "#Konum_Değişti", "📍", "Grup Konum Değişikliği",
                user_info, date
            )
            await self.send_log(log_text)

        # Görüşme Başladı
        elif isinstance(action, ChannelAdminLogEventActionStartGroupCall):
            log_text = LogFormatter.simple_log(
                "#Görüşme_Başladı", "📞", "Sesli/Görüntülü Görüşme Başlatıldı",
                user_info, date
            )
            await self.send_log(log_text)

        # Görüşme Bitti
        elif isinstance(action, ChannelAdminLogEventActionDiscardGroupCall):
            log_text = LogFormatter.simple_log(
                "#Görüşme_Bitti", "📴", "Sesli/Görüntülü Görüşme Sonlandırıldı",
                user_info, date
            )
            await self.send_log(log_text)

        # Görüşmede Ses Kapatıldı
        elif isinstance(action, ChannelAdminLogEventActionParticipantMute):
            target_id = action.participant.user_id if hasattr(action.participant, 'user_id') else None
            target_user = users_dict.get(target_id) if target_id else None
            target_info = get_user_info(target_user) if target_user else "Bilinmiyor"
            log_text = LogFormatter.simple_log(
                "#Görüşme_Ses_Kapatıldı", "🔇", "Görüşmede Ses Kapatma",
                user_info, date, **{"Sesi Kapatılan": target_info}
            )
            await self.send_log(log_text)

        # Görüşmede Ses Açıldı
        elif isinstance(action, ChannelAdminLogEventActionParticipantUnmute):
            target_id = action.participant.user_id if hasattr(action.participant, 'user_id') else None
            target_user = users_dict.get(target_id) if target_id else None
            target_info = get_user_info(target_user) if target_user else "Bilinmiyor"
            log_text = LogFormatter.simple_log(
                "#Görüşme_Ses_Açıldı", "🔊", "Görüşmede Ses Açma",
                user_info, date, **{"Sesi Açılan": target_info}
            )
            await self.send_log(log_text)

        # Görüşme Ayarları
        elif isinstance(action, ChannelAdminLogEventActionToggleGroupCallSetting):
            status = "Aktif" if action.join_muted else "Kapalı"
            log_text = LogFormatter.simple_log(
                "#Görüşme_Ayarı", "⚙", "Görüşme Ayar Değişikliği",
                user_info, date, **{"Katılımda Sesi Kapat": status}
            )
            await self.send_log(log_text)

        # Davet Linki Silindi
        elif isinstance(action, ChannelAdminLogEventActionExportedInviteDelete):
            link = action.invite.link if hasattr(action.invite, 'link') else "Bilinmiyor"
            log_text = LogFormatter.simple_log(
                "#Davet_Linki_Silindi", "🗑", "Davet Linki Silme",
                user_info, date, **{"Silinen Link": f"`{link}`"}
            )
            await self.send_log(log_text)

        # Davet Linki İptal
        elif isinstance(action, ChannelAdminLogEventActionExportedInviteRevoke):
            link = action.invite.link if hasattr(action.invite, 'link') else "Bilinmiyor"
            log_text = LogFormatter.simple_log(
                "#Davet_Linki_İptal", "🚫", "Davet Linki İptal Etme",
                user_info, date, **{"İptal Edilen Link": f"`{link}`"}
            )
            await self.send_log(log_text)

        # Davet Linki Düzenlendi
        elif isinstance(action, ChannelAdminLogEventActionExportedInviteEdit):
            log_text = LogFormatter.simple_log(
                "#Davet_Linki_Düzenlendi", "✏", "Davet Linki Düzenleme",
                user_info, date
            )
            await self.send_log(log_text)

        # Ses Seviyesi Değişti
        elif isinstance(action, ChannelAdminLogEventActionParticipantVolume):
            volume = action.participant.volume if hasattr(action.participant, 'volume') else 100
            log_text = LogFormatter.simple_log(
                "#Ses_Seviyesi_Değişti", "🔉", "Görüşmede Ses Seviyesi Değişikliği",
                user_info, date, **{"Yeni Seviye": f"%{volume // 100}"}
            )
            await self.send_log(log_text)

        # Otomatik Silme Süresi
        elif isinstance(action, ChannelAdminLogEventActionChangeHistoryTTL):
            log_text = LogFormatter.simple_log(
                "#Otomatik_Silme_Süresi", "⏱", "Otomatik Silme Süresi Değişikliği",
                user_info, date,
                **{
                    "Önceki Süre": format_ttl(action.prev_value),
                    "Yeni Süre": format_ttl(action.new_value)
                }
            )
            await self.send_log(log_text)

        # İletme Yasağı
        elif isinstance(action, ChannelAdminLogEventActionToggleNoForwards):
            status = "Aktif" if action.new_value else "Kapalı"
            emoji = "🚫" if action.new_value else "✅"
            tag = "#İletme_Yasağı_Açıldı" if action.new_value else "#İletme_Yasağı_Kapandı"
            log_text = LogFormatter.simple_log(
                tag, emoji, "İletme Yasağı Değişikliği",
                user_info, date, **{"Yeni Durum": status}
            )
            await self.send_log(log_text)

        # Mesaj Gönderildi
        elif isinstance(action, ChannelAdminLogEventActionSendMessage):
            await self._handle_send_message(action, user_info, date)

        # Tepkiler Değişti
        elif isinstance(action, ChannelAdminLogEventActionChangeAvailableReactions):
            log_text = LogFormatter.simple_log(
                "#Tepkiler_Değişti", "😀", "Tepki Ayarları Değişikliği",
                user_info, date
            )
            await self.send_log(log_text)

        # Kullanıcı Adları Değişti
        elif isinstance(action, ChannelAdminLogEventActionChangeUsernames):
            old = ", ".join(action.prev_value) if action.prev_value else "Yok"
            new = ", ".join(action.new_value) if action.new_value else "Yok"
            log_text = LogFormatter.simple_log(
                "#Kullanıcı_Adları_Değişti", "🔗", "Kullanıcı Adları Değişikliği",
                user_info, date, **{"Önceki": old, "Yeni": new}
            )
            await self.send_log(log_text)

        # Forum Modu
        elif isinstance(action, ChannelAdminLogEventActionToggleForum):
            status = "Aktif" if action.new_value else "Kapalı"
            tag = "#Forum_Modu_Açıldı" if action.new_value else "#Forum_Modu_Kapandı"
            log_text = LogFormatter.simple_log(
                tag, "💬", "Forum Modu Değişikliği",
                user_info, date, **{"Yeni Durum": status}
            )
            await self.send_log(log_text)

        # Konu Oluşturuldu
        elif isinstance(action, ChannelAdminLogEventActionCreateTopic):
            title = action.topic.title if hasattr(action.topic, 'title') else "Bilinmiyor"
            log_text = LogFormatter.simple_log(
                "#Konu_Oluşturuldu", "📁", "Yeni Konu Oluşturma",
                user_info, date, **{"Konu Başlığı": title}
            )
            await self.send_log(log_text)

        # Konu Düzenlendi
        elif isinstance(action, ChannelAdminLogEventActionEditTopic):
            title = action.new_topic.title if hasattr(action.new_topic, 'title') else "Bilinmiyor"
            log_text = LogFormatter.simple_log(
                "#Konu_Düzenlendi", "✏️", "Konu Düzenleme",
                user_info, date, **{"Konu Başlığı": title}
            )
            await self.send_log(log_text)

        # Konu Silindi
        elif isinstance(action, ChannelAdminLogEventActionDeleteTopic):
            title = action.topic.title if hasattr(action.topic, 'title') else "Bilinmiyor"
            log_text = LogFormatter.simple_log(
                "#Konu_Silindi", "🗑️", "Konu Silme",
                user_info, date, **{"Silinen Konu": title}
            )
            await self.send_log(log_text)

        # Konu Sabitleme
        elif isinstance(action, ChannelAdminLogEventActionPinTopic):
            log_text = LogFormatter.simple_log(
                "#Konu_Sabitleme", "📌", "Konu Sabitleme İşlemi",
                user_info, date
            )
            await self.send_log(log_text)

        # Bilinmeyen Eylem
        else:
            action_name = type(action).__name__.replace("ChannelAdminLogEventAction", "")
            log_text = LogFormatter.simple_log(
                "#Bilinmeyen_Eylem", "❓", "Tanımlanmamış Eylem",
                user_info, date, **{"Eylem Türü": action_name}
            )
            await self.send_log(log_text)

    # ============== YARDIMCI METODLAR ==============

    async def _handle_delete_message(self, action, user_info, date, users_dict):
        """Mesaj silme işlemi"""
        msg = action.message
        text = msg.message if msg.message else ""
        media_info = get_media_info(msg.media) if msg.media else ""

        msg_sender = users_dict.get(msg.from_id.user_id) if msg.from_id and hasattr(msg.from_id, 'user_id') else None
        msg_sender_info = get_user_info(msg_sender) if msg_sender else "Bilinmiyor"
        msg_date = format_date(msg.date) if msg.date else "Bilinmiyor"

        content_text = get_content_text(text, media_info)

        log_text = LogFormatter.message_deleted(
            user_info, msg_sender_info, content_text,
            msg_date, date, msg.id
        )

        if msg.media:
            try:
                file = await self.client.download_media(msg.media, bytes)
                await self.send_log(log_text, file=file)
            except:
                await self.send_log(log_text)
        else:
            await self.send_log(log_text)

    async def _handle_edit_message(self, action, user_info, date, users_dict):
        """Mesaj düzenleme işlemi"""
        old_msg = action.prev_message
        new_msg = action.new_message

        old_text = old_msg.message if old_msg.message else "İçerik yok"
        new_text = new_msg.message if new_msg.message else "İçerik yok"

        msg_sender = users_dict.get(new_msg.from_id.user_id) if new_msg.from_id and hasattr(new_msg.from_id, 'user_id') else None
        sender_info = get_user_info(msg_sender) if msg_sender else user_info

        log_text = LogFormatter.message_edited(
            sender_info, old_text, new_text, date, new_msg.id
        )
        await self.send_log(log_text)

    async def _handle_pin_message(self, action, user_info, date, users_dict):
        """Mesaj sabitleme işlemi"""
        msg = action.message
        text = msg.message if msg and msg.message else ""
        is_pinned = msg and msg.id

        msg_sender = users_dict.get(msg.from_id.user_id) if msg and msg.from_id and hasattr(msg.from_id, 'user_id') else None
        msg_sender_info = get_user_info(msg_sender) if msg_sender else "Bilinmiyor"
        media_info = get_media_info(msg.media) if msg and msg.media else ""

        content_text = get_content_text(text, media_info)

        log_text = LogFormatter.message_pinned(
            user_info, msg_sender_info, content_text,
            date, msg.id if msg else None, is_pinned
        )
        await self.send_log(log_text)

    async def _handle_join_by_invite(self, action, user_info, date, users_dict):
        """Link ile katılma işlemi"""
        invite = action.invite
        link = invite.link if hasattr(invite, 'link') else "Bilinmiyor"
        invite_admin = users_dict.get(invite.admin_id) if hasattr(invite, 'admin_id') and invite.admin_id else None
        invite_admin_info = get_user_info(invite_admin) if invite_admin else "Bilinmiyor"

        log_text = LogFormatter.simple_log(
            "#Link_İle_Katıldı", "🔗", "Davet Linki ile Katılma",
            user_info, date,
            **{"Kullanılan Link": f"`{link}`", "Linki Oluşturan": invite_admin_info}
        )
        await self.send_log(log_text)

    async def _handle_ban_toggle(self, action, user_info, date, users_dict):
        """Ban/kısıtlama işlemi"""
        target_user = users_dict.get(action.prev_participant.user_id) if hasattr(action.prev_participant, 'user_id') else None
        target_info = get_user_info(target_user) if target_user else "Bilinmiyor"

        new_rights = action.new_participant.banned_rights if hasattr(action.new_participant, 'banned_rights') else None
        old_rights = action.prev_participant.banned_rights if hasattr(action.prev_participant, 'banned_rights') else None

        if new_rights and new_rights.view_messages:
            action_type = 'ban'
        elif old_rights and old_rights.view_messages and (not new_rights or not new_rights.view_messages):
            action_type = 'unban'
        elif new_rights:
            action_type = 'restrict'
        else:
            action_type = 'unrestrict'

        new_restrictions = format_banned_rights(new_rights) if new_rights else "Yok"
        old_restrictions = format_banned_rights(old_rights) if old_rights else "Yok"

        until_text = ""
        if new_rights and new_rights.until_date:
            until_text = format_date(new_rights.until_date)

        log_text = LogFormatter.member_banned(
            user_info, target_info, old_restrictions, new_restrictions,
            until_text, date, action_type
        )
        await self.send_log(log_text)

    async def _handle_admin_toggle(self, action, user_info, date, users_dict):
        """Admin değişikliği işlemi"""
        target_id = action.new_participant.user_id if hasattr(action.new_participant, 'user_id') else None
        target_user = users_dict.get(target_id) if target_id else None
        target_info = get_user_info(target_user) if target_user else "Bilinmiyor"

        new_rights = action.new_participant.admin_rights if hasattr(action.new_participant, 'admin_rights') else None
        old_rights = action.prev_participant.admin_rights if hasattr(action.prev_participant, 'admin_rights') else None

        if new_rights and not old_rights:
            action_type = 'promote'
        elif old_rights and not new_rights:
            action_type = 'demote'
        else:
            action_type = 'change'

        new_perms = format_admin_rights(new_rights) if new_rights else "Yok"
        old_perms = format_admin_rights(old_rights) if old_rights else "Yok"

        rank = None
        if hasattr(action.new_participant, 'rank') and action.new_participant.rank:
            rank = action.new_participant.rank

        log_text = LogFormatter.admin_changed(
            user_info, target_info, old_perms, new_perms, rank, date, action_type
        )
        await self.send_log(log_text)

    async def _handle_photo_change(self, action, user_info, date):
        """Fotoğraf değişikliği işlemi"""
        photo_action = "Güncellendi" if action.new_photo else "Kaldırıldı"
        tag = "#Grup_Fotoğrafı_Değişti" if action.new_photo else "#Grup_Fotoğrafı_Kaldırıldı"

        log_text = LogFormatter.simple_log(
            tag, "🖼", "Grup Fotoğrafı Değişikliği",
            user_info, date, **{"İşlem": f"Fotoğraf {photo_action}"}
        )

        if action.new_photo:
            try:
                file = await self.client.download_media(action.new_photo, bytes)
                await self.send_log(log_text, file=file)
            except:
                await self.send_log(log_text)
        else:
            await self.send_log(log_text)

    async def _handle_send_message(self, action, user_info, date):
        """Mesaj gönderme işlemi"""
        msg = action.message
        text = msg.message if msg.message else ""
        media_info = get_media_info(msg.media) if msg.media else ""

        log_text = LogFormatter.simple_log(
            "#Mesaj_Gönderildi", "📤", "Mesaj Gönderme İşlemi",
            user_info, date,
            **{
                "Mesaj İçeriği": text if text else "(Metin yok)",
                "Medya": media_info if media_info else None,
                "Mesaj ID": f"`{msg.id}`"
            }
        )

        if msg.media:
            try:
                file = await self.client.download_media(msg.media, bytes)
                await self.send_log(log_text, file=file)
            except:
                await self.send_log(log_text)
        else:
            await self.send_log(log_text)
