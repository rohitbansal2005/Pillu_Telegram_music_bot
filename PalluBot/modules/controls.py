from pyrogram import filters, Client
from pyrogram.types import Message, CallbackQuery
from pyrogram.enums import ChatMemberStatus
from PalluBot import app, call_py
from PalluBot.utils.queue import get_queue, clear_queue, remove_from_queue, pop_from_queue, active_progress_tasks
from pytgcalls.types import MediaStream, AudioQuality

async def is_admin(client: Client, chat_id: int, user_id: int) -> bool:
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except:
        return False

@app.on_message(filters.command(["pause"]) & filters.group)
async def pause_cmd(client: Client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply_text("❌ **Only Admins can use this command!**")
    if not call_py:
        return
    try:
        await call_py.pause(message.chat.id)
        await message.reply_text("⏸ **Music Paused!**")
    except Exception as e:
        await message.reply_text("❌ Not playing anything.")

@app.on_message(filters.command(["resume"]) & filters.group)
async def resume_cmd(client: Client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply_text("❌ **Only Admins can use this command!**")
    if not call_py:
        return
    try:
        await call_py.resume(message.chat.id)
        await message.reply_text("▶️ **Music Resumed!**")
    except Exception as e:
        await message.reply_text("❌ Not paused.")

@app.on_message(filters.command(["skip"]) & filters.group)
async def skip_cmd(client: Client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply_text("❌ **Only Admins can use this command!**")
    if not call_py:
        return
    chat_id = message.chat.id
    queue = get_queue(chat_id)
    if len(queue) > 1:
        pop_from_queue(chat_id)
        next_song = queue[0]
        
        # RE-FETCH URL TO PREVENT EXPIRATION
        from PalluBot.utils.youtube import get_yt_info
        try:
            fresh_info = await get_yt_info(next_song.get("query", next_song["title"]))
            if fresh_info and fresh_info.get("url"):
                next_song["stream_url"] = fresh_info.get("url")
        except Exception as refetch_err:
            pass

        try:
            if chat_id in active_progress_tasks:
                active_progress_tasks[chat_id].cancel()
            await call_py.play(chat_id, MediaStream(next_song["stream_url"], audio_parameters=AudioQuality.LOW))
            
            from PalluBot.utils.theme import format_playing_message, play_keyboard
            from PalluBot.modules.play import update_progress_bar
            import asyncio
            
            sent_msg = await message.reply_photo(
                photo=next_song.get("thumbnail", "https://graph.org/file/857a2fbb08d95e0c52136.jpg"),
                caption=format_playing_message(
                    next_song["title"], 
                    next_song["duration"], 
                    next_song["requested_by"],
                    0, 0
                ),
                reply_markup=play_keyboard()
            )
            
            active_progress_tasks[chat_id] = asyncio.create_task(update_progress_bar(chat_id, sent_msg, next_song))
        except Exception as e:
            await message.reply_text(f"❌ Error skipping: {e}")
    else:
        try:
            if chat_id in active_progress_tasks:
                active_progress_tasks[chat_id].cancel()
            clear_queue(chat_id)
            await call_py.leave_call(chat_id)
            await message.reply_text("⏭ **Skipped!** No more songs in queue, leaving voice chat.")
        except:
            pass

@app.on_message(filters.command(["stop"]) & filters.group)
async def stop_cmd(client: Client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply_text("❌ **Only Admins can use this command!**")
    if not call_py:
        return
    chat_id = message.chat.id
    try:
        if chat_id in active_progress_tasks:
            active_progress_tasks[chat_id].cancel()
        clear_queue(chat_id)
        await call_py.leave_call(chat_id)
        await message.reply_text("⏹ **Music Stopped & Queue Cleared!**")
    except Exception as e:
        await message.reply_text("❌ Not playing anything.")

# Callback Queries for Inline Keyboard
@app.on_callback_query(filters.regex("^(pause|resume|skip|stop|close_panel)$"))
async def callbacks(client: Client, callback_query: CallbackQuery):
    chat_id = callback_query.message.chat.id
    user_id = callback_query.from_user.id
    
    if callback_query.data == "close_panel":
        return await callback_query.message.delete()
        
    if not await is_admin(client, chat_id, user_id):
        return await callback_query.answer("❌ Only Admins can use this button!", show_alert=True)
        
    data = callback_query.data
    try:
        if data == "pause":
            await call_py.pause(chat_id)
            await callback_query.answer("Music Paused!", show_alert=False)
        elif data == "resume":
            await call_py.resume(chat_id)
            await callback_query.answer("Music Resumed!", show_alert=False)
        elif data == "skip":
            queue = get_queue(chat_id)
            if chat_id in active_progress_tasks:
                active_progress_tasks[chat_id].cancel()
            if len(queue) > 1:
                pop_from_queue(chat_id)
                next_song = queue[0]
                await call_py.play(chat_id, MediaStream(next_song["stream_url"]))
                await callback_query.answer("Skipped!", show_alert=False)
            else:
                clear_queue(chat_id)
                await call_py.leave_call(chat_id)
                await callback_query.answer("Skipped! No more songs.", show_alert=False)
        elif data == "stop":
            if chat_id in active_progress_tasks:
                active_progress_tasks[chat_id].cancel()
            clear_queue(chat_id)
            await call_py.leave_call(chat_id)
            await callback_query.answer("Music Stopped!", show_alert=False)
    except Exception as e:
        print(f"Callback Error: {e}")
        await callback_query.answer(f"Action failed: {e}", show_alert=True)
