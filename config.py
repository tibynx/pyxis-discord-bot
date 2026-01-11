"""Configuration for the Discord bot."""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def _get_int(name: str, default: int = None) -> int:
    val = os.getenv(name)
    if val is None:
        return default
    try:
        return int(val)
    except ValueError:
        return default

BOT_TOKEN = os.getenv('BOT_TOKEN')
SYNC_GUILD = _get_int('SYNC_GUILD')
TARGET_GUILD = _get_int('TARGET_GUILD')  # Target server for invite links
TARGET_CHANNEL = _get_int('TARGET_CHANNEL')  # Target channel for invite links
INVITE_TIMEOUT = _get_int('INVITE_TIMEOUT', 600)  # Timeout for invites, default 10 minutes
ONLINE_MEMBER_INDICATOR = os.getenv('ONLINE_MEMBER_INDICATOR', '🟢 ')
TOTAL_MEMBER_INDICATOR = os.getenv('TOTAL_MEMBER_INDICATOR', '⚪ ')
