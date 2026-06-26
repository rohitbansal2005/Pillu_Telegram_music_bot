from pyrogram import Client
from pytgcalls import PyTgCalls
from config import API_ID, API_HASH, BOT_TOKEN, SESSION_STRING

# Initialize Bot
app = Client(
    "PalluBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="PalluBot.modules")
)

# Initialize Assistant
if SESSION_STRING:
    assistant = Client(
        "PalluAssistant",
        api_id=API_ID,
        api_hash=API_HASH,
        session_string=SESSION_STRING
    )
    call_py = PyTgCalls(assistant)
else:
    assistant = None
    call_py = None
