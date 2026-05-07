"""
Harley Telegram Bot - Event Tipleri
====================================
"""

from enum import Enum, auto


class EventType(Enum):
    """Bot event tipleri"""
    # Mesaj işlemleri
    MESSAGE_DELETED = auto()
    MESSAGE_EDITED = auto()
    MESSAGE_PINNED = auto()
    MESSAGE_UNPINNED = auto()
    MESSAGE_SENT = auto()

    # Üye işlemleri
    MEMBER_JOINED = auto()
    MEMBER_LEFT = auto()
    MEMBER_INVITED = auto()
    MEMBER_JOINED_BY_LINK = auto()
    MEMBER_JOINED_BY_REQUEST = auto()
    MEMBER_KICKED = auto()
    MEMBER_BANNED = auto()
    MEMBER_UNBANNED = auto()
    MEMBER_RESTRICTED = auto()
    MEMBER_UNRESTRICTED = auto()

    # Admin işlemleri
    ADMIN_PROMOTED = auto()
    ADMIN_DEMOTED = auto()
    ADMIN_RIGHTS_CHANGED = auto()

    # Grup ayarları
    GROUP_TITLE_CHANGED = auto()
    GROUP_ABOUT_CHANGED = auto()
    GROUP_USERNAME_CHANGED = auto()
    GROUP_PHOTO_CHANGED = auto()
    GROUP_INVITES_TOGGLED = auto()
    GROUP_SIGNATURES_TOGGLED = auto()
    GROUP_SLOW_MODE_TOGGLED = auto()
    GROUP_HISTORY_HIDDEN_TOGGLED = auto()
    GROUP_DEFAULT_RIGHTS_CHANGED = auto()
    GROUP_STICKER_SET_CHANGED = auto()
    GROUP_LINKED_CHAT_CHANGED = auto()
    GROUP_LOCATION_CHANGED = auto()
    GROUP_NO_FORWARDS_TOGGLED = auto()
    GROUP_REACTIONS_CHANGED = auto()
    GROUP_USERNAMES_CHANGED = auto()
    GROUP_HISTORY_TTL_CHANGED = auto()

    # Forum işlemleri
    FORUM_TOGGLED = auto()
    TOPIC_CREATED = auto()
    TOPIC_EDITED = auto()
    TOPIC_DELETED = auto()
    TOPIC_PINNED = auto()

    # Görüşme işlemleri
    GROUP_CALL_STARTED = auto()
    GROUP_CALL_ENDED = auto()
    PARTICIPANT_MUTED = auto()
    PARTICIPANT_UNMUTED = auto()
    PARTICIPANT_VOLUME_CHANGED = auto()
    GROUP_CALL_SETTINGS_CHANGED = auto()

    # Davet linki işlemleri
    INVITE_LINK_DELETED = auto()
    INVITE_LINK_REVOKED = auto()
    INVITE_LINK_EDITED = auto()

    # Anket işlemleri
    POLL_STOPPED = auto()

    # Bilinmeyen
    UNKNOWN = auto()


class BotState(Enum):
    """Bot durumları"""
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


class ModuleState(Enum):
    """Modül durumları"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    CLEARING = "clearing"
    ERROR = "error"
