import os

from dotenv import load_dotenv

# Load data from .env file
load_dotenv()

API_ID: int = int(os.getenv("API_ID"))  # Telegram api id
API_HASH: str = os.getenv("API_HASH")  # Telegram api hash
SESSION_STRING: str = os.getenv("SESSION_STRING")  # Session string (get it from login.py)


# Database configs

DB_CONNECTION_STRING: str = os.getenv("DB_CONNECTION_STRING")  # String for connect to MongoDB


# Bot configs
BOT_API: str = os.getenv("BOT_API")



