import asyncio
from pyrogram import filters, Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pytgcalls.types import MediaStream, AudioQuality
from PalluBot import app, call_py, assistant
from PalluBot.utils.youtube import get_yt_info
from PalluBot.utils.queue import add_to_queue, active_progress_tasks
from PalluBot.utils.theme import format_playing_message, play_keyboard
from PalluBot.modules.play import update_progress_bar

@app.on_callback_query(filters.regex(r"^play_sugg_(.*)$"))
async def play_suggestion(client: Client, query):
    track = query.matches[0].group(1)
    await query.answer("Fetching track...")
    await query.message.edit_text(f"🔍 **Playing suggested track:** {track}...")
    
    try:
        song_info_data = await get_yt_info(track)
        if not song_info_data:
            return await query.message.edit_text("❌ Could not load the suggested track.")
            
        stream_url = song_info_data.get('url')
        if not stream_url:
            return await query.message.edit_text("❌ Failed to extract audio URL.")
            
        chat_id = query.message.chat.id
        song_info = {
            "title": song_info_data.get('title'),
            "duration": song_info_data.get('duration'),
            "url": "https://www.jiosaavn.com",
            "stream_url": stream_url,
            "thumbnail": song_info_data.get("thumbnail", "https://graph.org/file/857a2fbb08d95e0c52136.jpg"),
            "requested_by": query.from_user.mention,
            "query": track
        }
        
        # Ensure assistant is in chat
        from pyrogram.errors import PeerIdInvalid, UserAlreadyParticipant
        try:
            await assistant.get_chat(chat_id)
        except PeerIdInvalid:
            try:
                try:
                    await app.add_chat_members(chat_id, assistant.me.id)
                except Exception:
                    if query.message.chat.username:
                        await assistant.join_chat(query.message.chat.username)
                    else:
                        invite_link = await app.export_chat_invite_link(chat_id)
                        await assistant.join_chat(invite_link)
            except Exception:
                pass
        except Exception:
            pass
            
        add_to_queue(chat_id, song_info)
        await call_py.play(
            chat_id,
            MediaStream(stream_url, audio_parameters=AudioQuality.LOW)
        )
        await query.message.delete()
        sent_msg = await app.send_photo(
            chat_id,
            photo=song_info["thumbnail"],
            caption=format_playing_message(song_info["title"], song_info["duration"], query.from_user.mention, 0, 0),
            reply_markup=play_keyboard()
        )
        if chat_id in active_progress_tasks:
            active_progress_tasks[chat_id].cancel()
        active_progress_tasks[chat_id] = asyncio.create_task(update_progress_bar(chat_id, sent_msg, song_info))
    except Exception as e:
        await query.message.edit_text(f"❌ **Error:** `{str(e)}`")

@app.on_callback_query(filters.regex("^more_songs$"))
async def more_songs_callback(client: Client, query):
    import random
    popular_tracks = [
        "Tum Hi Ho", "Chaleya", "Kesariya", "Agar Tum Saath Ho", 
        "Heeriye", "O Maahi", "Apna Bana Le", "Pee Loon", 
        "Khairiyat", "Raabta", "Heat Waves", "Perfect",
        "Tu Hi Haqeeqat", "Jeene Laga Hoon", "Kabira", "Zaalima",
        "Tere Hawale", "Maan Meri Jaan", "Satranga", "Arjan Vailly"
    ]
    suggestions = random.sample(popular_tracks, 3)
    
    buttons = []
    for track in suggestions:
        buttons.append([InlineKeyboardButton(f"🎵 {track}", callback_data=f"play_sugg_{track}")])
    buttons.append([InlineKeyboardButton("More Songs?", callback_data="more_songs")])
    
    await query.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(buttons))
