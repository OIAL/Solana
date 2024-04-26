import os

from dotenv import load_dotenv

# Load data from .env file
load_dotenv()

API_ID: int = int(os.getenv("API_ID"))  # Telegram api id
API_HASH: str = os.getenv("API_HASH")  # Telegram api hash
SESSION_STRING: str = os.getenv("SESSION_STRING")  # Session string (get it from login.py)
OUTPUT_CHAT_ID: int = int(os.getenv("OUTPUT_CHAT_ID"))
TRANSACTIONS_SCANNING_TIME_MINUTES: str = os.getenv("TRANSACTIONS_SCANNING_TIME_MINUTES")
TOKENS_LIMIT: int = int(os.getenv("TOKENS_LIMIT"))
SOLANA_TOKENS_IGNORE_RANGE: list[float] = [
    float(os.getenv("SOLANA_TOKENS_IGNORE_RANGE").split(";")[0]),
    float(os.getenv("SOLANA_TOKENS_IGNORE_RANGE").split(";")[1])
]

# Database configs
DB_CONNECTION_STRING: str = os.getenv("DB_CONNECTION_STRING")  # String for connect to MongoDB
DB_COLLECTION_NAME: str = os.getenv("DB_COLLECTION_NAME")

# Bot configs
BOT_API: str = os.getenv("BOT_API")
TOKEN_HANDLE_TIME_MINUTES: int = 60

HELIUS_API_KEY: str = os.getenv("HELIUS_API_KEY")
INTERPRETER_PATH: str = os.getenv("INTERPRETER_PATH")
SCANNER_FILE_PATH: str = os.getenv("SCANNER_FILE_PATH")
