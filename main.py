import asyncio
import os
import sys

# Add current directory to PATH for ffmpeg/ffprobe
os.environ["PATH"] += os.pathsep + os.path.dirname(os.path.abspath(__file__))

from pyrogram.types import BotCommand
import pyrogram.errors
import pyrogram.raw.types
import sys

class DummyType: pass

class MissingTypesHandler:
    def __init__(self, original_module):
        self.original_module = original_module
    def __getattr__(self, item):
        if hasattr(self.original_module, item):
            return getattr(self.original_module, item)
        return DummyType

sys.modules['pyrogram.raw.types'] = MissingTypesHandler(pyrogram.raw.types)
pyrogram.raw.types = sys.modules['pyrogram.raw.types']

class DummyException(Exception): pass
if not hasattr(pyrogram.errors, 'GroupcallForbidden'):
    pyrogram.errors.GroupcallForbidden = DummyException
if not hasattr(pyrogram.errors, 'GroupcallInvalid'):
    pyrogram.errors.GroupcallInvalid = DummyException

from pyrogram.raw.functions.phone import JoinGroupCall
_old_join_init = JoinGroupCall.__init__
def _new_join_init(self, *args, **kwargs):
    kwargs.pop("public_key", None)
    _old_join_init(self, *args, **kwargs)
JoinGroupCall.__init__ = _new_join_init


from pyrogram import idle
from PalluBot import app, call_py, assistant
from keep_alive import keep_alive

async def start_bot():
    keep_alive() # Start the flask server for Render
    print("Starting Pallu Bot Client...")
    await app.start()
    
    print("Starting Assistant Client...")
    if assistant:
        await assistant.start()
    
    print("Starting PyTgCalls Client...")
    if call_py:
        await call_py.start()
        
    print("\nPallu Music Bot is now running!")
    
    try:
        await app.set_bot_commands([
            BotCommand("play", "Play a song in voice chat"),
            BotCommand("pause", "Pause the current song"),
            BotCommand("resume", "Resume the paused song"),
            BotCommand("skip", "Skip to the next song in queue"),
            BotCommand("stop", "Stop playing and clear queue"),
        ])
    except Exception as e:
        print(f"Failed to set bot commands: {e}")
        
    await idle()
    print("Stopping Pallu Music Bot...")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_bot())
