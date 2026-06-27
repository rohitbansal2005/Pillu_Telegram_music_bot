from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import math

def get_progress_bar(played_seconds: int, total_seconds: int) -> str:
    # Handle Live streams (total_seconds = 0 or unknown)
    if total_seconds <= 0:
        return "00:00 🔘────────────── LIVE"
        
    percentage = played_seconds / total_seconds
    # 15 segments total
    filled_blocks = int(percentage * 15)
    
    if filled_blocks > 14:
        filled_blocks = 14
        
    bar = "─" * filled_blocks + "🔘" + "─" * (14 - filled_blocks)
    
    # Format times MM:SS
    played_m = played_seconds // 60
    played_s = played_seconds % 60
    total_m = total_seconds // 60
    total_s = total_seconds % 60
    
    return f"{played_m:02d}:{played_s:02d} {bar} {total_m:02d}:{total_s:02d}"

def play_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(text="⏸ Pause", callback_data="pause"),
            InlineKeyboardButton(text="▶️ Resume", callback_data="resume")
        ],
        [
            InlineKeyboardButton(text="⏭ Skip", callback_data="skip"),
            InlineKeyboardButton(text="⏹ Stop", callback_data="stop")
        ]
    ])

def queue_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(text="🥂 CLOSE", callback_data="close_panel")
        ]
    ])

def format_playing_message(title: str, duration: str, requested_by: str, played_seconds: int = 0, total_seconds: int = 0) -> str:
    short_title = title[:35] + "..." if len(title) > 35 else title
    
    if total_seconds > 0:
        timeline = get_progress_bar(played_seconds, total_seconds)
    else:
        # Fallback if no total_seconds provided
        timeline = f"00:00 🔘────────────── {duration}"
    
    return f"""
✨ **NOW PLAYING** ✨

🎵 **Title:** {short_title}
🙋‍♂️ **Requested By:** {requested_by}

`{timeline}`

**Powered by Pallu Music 🎶**
**Developed by @rootpii**
"""
