from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from PalluBot import app

@app.on_message(filters.command(["start", "help"]) & filters.private)
async def start_command(client: Client, message: Message):
    # Try to get user's profile photo
    user_id = message.from_user.id
    user_photo = None
    
    # Check if user has a profile photo
    async for photo in client.get_chat_photos(user_id, limit=1):
        user_photo = photo.file_id
        break
        
    # Fallback to a default music image if user has no DP
    if not user_photo:
        user_photo = "https://telegra.ph/file/857a2fbb08d95e0c52136.jpg"

    caption = (
        f"Hey there, {message.from_user.mention}! 👋\n\n"
        "Welcome to **Pallu Music Bot** 🎵\n"
        "A fast, powerful, and seamless music bot for Telegram Voice Chats.\n\n"
        "✨ **Features:**\n"
        "• Play from YouTube, Spotify & more\n"
        "• High Quality Audio (HD)\n"
        "• Zero Lag & 24/7 Uptime\n\n"
        "Tap the buttons below to explore more!"
    )

    bot_username = (await client.get_me()).username

    reply_markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "➕ Add Bot to your Group ➕", 
                url=f"https://t.me/{bot_username}?startgroup=true"
            )
        ],
        [
            InlineKeyboardButton("ꜱᴏᴜʀᴄᴇ", url="https://github.com/rootpiii"),
            InlineKeyboardButton("ᴅᴇᴠᴇʟᴏᴘᴇʀ", url="https://t.me/rootpii")
        ],
        [
            InlineKeyboardButton("📚 Commands", callback_data="help_commands")
        ]
    ])

    await message.reply_photo(
        photo=user_photo,
        caption=caption,
        reply_markup=reply_markup
    )

@app.on_callback_query(filters.regex("help_commands"))
async def help_callback(client: Client, query):
    help_text = (
        "**📚 Pallu Music Commands:**\n\n"
        "🎵 `/play <song>` - Play music in voice chat\n"
        "⏸ `/pause` - Pause the current music\n"
        "▶️ `/resume` - Resume the paused music\n"
        "⏭ `/skip` - Skip to the next song\n"
        "⏹ `/stop` - Stop the music and clear the queue"
    )
    await query.answer()
    await query.message.edit_caption(
        caption=help_text,
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("⬅️ Back", callback_data="start_menu")
        ]])
    )

@app.on_callback_query(filters.regex("start_menu"))
async def start_menu_callback(client: Client, query):
    caption = (
        f"Hey there, {query.from_user.mention}! 👋\n\n"
        "Welcome to **Pallu Music Bot** 🎵\n"
        "A fast, powerful, and seamless music bot for Telegram Voice Chats.\n\n"
        "✨ **Features:**\n"
        "• Play from YouTube, Spotify & more\n"
        "• High Quality Audio (HD)\n"
        "• Zero Lag & 24/7 Uptime\n\n"
        "Tap the buttons below to explore more!"
    )
    bot_username = (await client.get_me()).username
    reply_markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "➕ Add Bot to your Group ➕", 
                url=f"https://t.me/{bot_username}?startgroup=true"
            )
        ],
        [
            InlineKeyboardButton("ꜱᴏᴜʀᴄᴇ", url="https://github.com/rootpiii"),
            InlineKeyboardButton("ᴅᴇᴠᴇʟᴏᴘᴇʀ", url="https://t.me/rootpii")
        ],
        [
            InlineKeyboardButton("📚 Commands", callback_data="help_commands")
        ]
    ])
    await query.answer()
    await query.message.edit_caption(caption=caption, reply_markup=reply_markup)
