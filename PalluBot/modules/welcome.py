from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from PalluBot import app

@app.on_message(filters.new_chat_members & filters.group)
async def welcome_new_member(client: Client, message: Message):
    print("New chat member event triggered!")
    try:
        for member in message.new_chat_members:
            if member.is_bot:
                print(f"Ignored bot: {member.first_name}")
                continue
                
            print(f"Welcoming user: {member.first_name}")
            user_id = member.id
            user_photo = None
            
            try:
                async for photo in client.get_chat_photos(user_id, limit=1):
                    user_photo = photo.file_id
                    break
            except Exception as e:
                print(f"Error fetching photo: {e}")
                
            if not user_photo:
                user_photo = "https://graph.org/file/857a2fbb08d95e0c52136.jpg"
                
            chat_name = message.chat.title
            
            caption = (
                f"🌸 ─── ✧ ─── ✧ ─── 🌸\n\n"
                f"🎉 **WELCOME TO OUR FAMILY!** 🎉\n\n"
                f"👤 **Name:** {member.mention}\n"
                f"🔖 **Username:** @{member.username if member.username else 'N/A'}\n"
                f"🆔 **User ID:** `{user_id}`\n"
                f"🏠 **Group:** {chat_name}\n\n"
                f"💖 We're so happy to have you here!\n"
                f"🎵 Enjoy the best music experience with Pallu Music.\n\n"
                f"🌸 ─── ✧ ─── ✧ ─── 🌸"
            )
            
            bot_me = await client.get_me()
            bot_username = bot_me.username
            
            reply_markup = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "➕ Add Bot To Your Group ➕", 
                        url=f"https://t.me/{bot_username}?startgroup=true"
                    )
                ]
            ])
            
            try:
                await message.reply_photo(
                    photo=user_photo,
                    caption=caption,
                    reply_markup=reply_markup
                )
            except Exception as photo_err:
                print(f"Photo failed, falling back to text: {photo_err}")
                await message.reply_text(
                    text=caption,
                    reply_markup=reply_markup
                )
                
            print("Welcome message sent successfully!")
    except Exception as e:
        print(f"Welcome module error: {e}")
