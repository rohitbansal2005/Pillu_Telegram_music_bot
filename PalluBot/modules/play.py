import pyrogram
from pyrogram import filters, Client
from pyrogram.types import Message
from pytgcalls.types import MediaStream, Update, AudioQuality
from PalluBot import app, call_py
from PalluBot.utils.youtube import get_yt_info, search_youtube
from PalluBot.utils.queue import add_to_queue, get_queue, pop_from_queue, clear_queue, remove_from_queue, active_progress_tasks
from PalluBot.utils.theme import play_keyboard, format_playing_message, queue_keyboard
import asyncio
from pyrogram.errors import MessageNotModified

async def update_progress_bar(chat_id: int, message: Message, song_info: dict):
    duration_str = song_info.get("duration", "0:00")
    if duration_str == "Unknown" or not duration_str:
        return
        
    parts = duration_str.split(":")
    try:
        if len(parts) == 2:
            total_seconds = int(parts[0]) * 60 + int(parts[1])
        elif len(parts) == 3:
            total_seconds = int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        else:
            total_seconds = 0
    except:
        total_seconds = 0
        
    if total_seconds <= 0:
        return

    played_seconds = 0
    while played_seconds < total_seconds:
        await asyncio.sleep(60)
        played_seconds += 60
        if played_seconds > total_seconds:
            played_seconds = total_seconds
            
        try:
            await message.edit_caption(
                caption=format_playing_message(
                    song_info["title"], 
                    song_info["duration"], 
                    song_info["requested_by"], 
                    played_seconds, 
                    total_seconds
                ),
                reply_markup=play_keyboard()
            )
        except MessageNotModified:
            pass
        except Exception:
            break

@app.on_message(filters.command(["play", "pallu"]))
async def play_command(client: Client, message: Message):
    if message.chat.type == pyrogram.enums.ChatType.PRIVATE:
        return await message.reply_text("❌ **Please use this command in a Group Chat!** I need to join a Voice Chat to play music.")

    if not call_py:
        return await message.reply_text("Assistant session is not configured.")

    if len(message.command) < 2:
        return await message.reply_text("Please provide a song name. Example: `/play heat waves`")

    query = " ".join(message.command[1:])
    processing_msg = await message.reply_text("🔍 **Searching for your song on JioSaavn...**")

    try:
        # Step 1: Get high quality audio stream URL via JioSaavn
        song_info_data = await get_yt_info(query)
        
        if not song_info_data:
            await processing_msg.edit_text("❌ Song could not be found or extracted. Please try another query.")
            return
            
        stream_url = song_info_data.get('url')
        if not stream_url:
            return await processing_msg.edit_text("❌ **Failed to extract audio URL.**")

        title = song_info_data.get('title')
        duration = song_info_data.get('duration')
        
        chat_id = message.chat.id
        thumbnail = song_info_data.get("thumbnail", "https://telegra.ph/file/857a2fbb08d95e0c52136.jpg")
        song_info = {
            "title": title,
            "duration": duration,
            "url": "https://www.jiosaavn.com",
            "stream_url": stream_url,
            "thumbnail": thumbnail,
            "requested_by": message.from_user.mention
        }

        # Step 3: Check if something is already playing
        queue = get_queue(chat_id)
        if len(queue) > 0:
            position = len(queue)
            add_to_queue(chat_id, song_info)
            await processing_msg.delete()
            
            queue_msg = (
                f"⌈Pallu 🎵 Music▷⌋\n"
                f"➲ ADDED TO QUEUE AT #{position}\n\n"
                f"▸ **TITLE :** {title}\n"
                f"▸ **DURATION :** {duration} MINUTES\n"
                f"▸ **REQUESTED BY :** {message.from_user.mention}"
            )
            
            await message.reply_text(
                text=queue_msg,
                reply_markup=queue_keyboard()
            )
        else:
            # Play directly
            add_to_queue(chat_id, song_info)
            try:
                await call_py.play(
                    chat_id,
                    MediaStream(
                        stream_url,
                        audio_parameters=AudioQuality.HIGH
                    )
                )
                
                await processing_msg.delete()
                sent_msg = await message.reply_photo(
                    photo=thumbnail,
                    caption=format_playing_message(title, duration, message.from_user.mention, 0, 0),
                    reply_markup=play_keyboard()
                )
                
                if chat_id in active_progress_tasks:
                    active_progress_tasks[chat_id].cancel()
                active_progress_tasks[chat_id] = asyncio.create_task(update_progress_bar(chat_id, sent_msg, song_info))
            except Exception as e:
                remove_from_queue(chat_id)
                await processing_msg.edit_text(f"❌ **Error joining Voice Chat:**\n`{str(e)}`")

    except Exception as e:
        await processing_msg.edit_text(f"❌ **An error occurred:** `{str(e)}`")

from pytgcalls import filters as ptc_filters

@call_py.on_update(ptc_filters.stream_end)
async def stream_end_handler(client, update: Update):
    chat_id = update.chat_id
    # Remove the currently playing song
    pop_from_queue(chat_id)
    
    # Check for next song
    queue = get_queue(chat_id)
    if len(queue) > 0:
        next_song = queue[0]
        await call_py.play(
            chat_id,
            MediaStream(
                next_song["stream_url"],
                audio_parameters=AudioQuality.HIGH
            )
        )
        sent_msg = await app.send_photo(
            chat_id,
            photo=next_song.get("thumbnail", "https://telegra.ph/file/857a2fbb08d95e0c52136.jpg"),
            caption=format_playing_message(
                next_song["title"], 
                next_song["duration"], 
                next_song["requested_by"],
                0, 0
            ),
            reply_markup=play_keyboard()
        )
        if chat_id in active_progress_tasks:
            active_progress_tasks[chat_id].cancel()
        active_progress_tasks[chat_id] = asyncio.create_task(update_progress_bar(chat_id, sent_msg, next_song))
    else:
        # No more songs, leave call
        await call_py.leave_call(chat_id)
        remove_from_queue(chat_id)
