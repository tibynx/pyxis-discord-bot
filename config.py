"""Configuration for the Discord bot."""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
SYNC_GUILD = os.getenv('SYNC_GUILD')
TARGET_GUILD = os.getenv('TARGET_GUILD')  # Target server for invite links
TARGET_CHANNEL = os.getenv('TARGET_CHANNEL')  # Target channel for invite links
INVITE_TIMEOUT = int(os.getenv('INVITE_TIMEOUT', 600))  # Timeout for invites, default 10 minutes
ONLINE_MEMBER_INDICATOR = os.getenv('ONLINE_MEMBER_INDICATOR', '🟢 ')
TOTAL_MEMBER_INDICATOR = os.getenv('TOTAL_MEMBER_INDICATOR', '⚪ ')