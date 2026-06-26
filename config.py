import os
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID", 0))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
SESSION_STRING = os.getenv("SESSION_STRING")

# Optional Log Group
LOG_GROUP_ID = os.getenv("LOG_GROUP_ID")
if LOG_GROUP_ID:
    LOG_GROUP_ID = int(LOG_GROUP_ID)
