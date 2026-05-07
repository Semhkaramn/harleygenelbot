"""
Harley Telegram Bot - Admin Log Action İşleyiciler
===================================================
"""
import logging
from typing import Dict, Any
from telethon.tl.types import *
from ...utils.helpers import get_user_info, format_date, get_media_info, get_content_text
from ...utils.formatters import format_banned_rights, format_admin_rights
from .formatter import LogFormatter

logger = logging.getLogger(__name__)

class AdminLogActionProcessor:
    def __init__(self, client, send_log_callback):
        self.client = client
        self.send_log = send_log_callback
