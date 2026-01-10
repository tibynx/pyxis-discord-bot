"""Configuration for the Discord bot."""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
SYNC_GUILD = os.getenv('SYNC_GUILD')
