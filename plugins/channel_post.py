#(©)Codexbotz

import asyncio
from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait

from bot import Bot
from config import ADMINS, CHANNEL_ID, DISABLE_CHANNEL_BUTTON
from helper_func import encode

# Import the URL shortener from link_generator
from plugins.link_generator import url_shortener

@Bot.on_message(filters.private & filters.user(ADMINS) & ~filters.command(['start','users','broadcast','batch','genlink','stats']))
async def channel_post(client: Client, message: Message):
    reply_text = await message.reply_text("Please Wait...!", quote = True)
    try:
        post_message = await message.copy(chat_id = client.db_channel.id, disable_notification=True)
    except FloodWait as e:
        await asyncio.sleep(e.x)
        post_message = await message.copy(chat_id = client.db_channel.id, disable_notification=True)
    except Exception as e:
        print(e)
        await reply_text.edit_text("Something went Wrong..!")
        return
    
    converted_id = post_message.id * abs(client.db_channel.id)
    string = f"get-{converted_id}"
    base64_string = await encode(string)
    link = f"https://t.me/{client.username}?start={base64_string}"
    
    # Generate short URL
    short_url = url_shortener.shorten_url(link)
    
    # Create inline keyboard with multiple buttons
    buttons = [
        [
            InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}'),
            InlineKeyboardButton("🔗 Short URL", url=short_url) if short_url else None
        ]
    ]
    # Remove None values from buttons
    buttons = [list(filter(None, row)) for row in buttons]
    
    reply_markup = InlineKeyboardMarkup(buttons)

    await reply_text.edit(
        f"<b>Here is your link</b>\n\n{link}\n\n<b>Short URL:</b> {short_url or 'Unable to generate'}", 
        reply_markup=reply_markup, 
        disable_web_page_preview=True
    )

    if not DISABLE_CHANNEL_BUTTON:
        await post_message.edit_reply_markup(reply_markup)

@Bot.on_message(filters.channel & filters.incoming & filters.chat(CHANNEL_ID))
async def new_post(client: Client, message: Message):
    if DISABLE_CHANNEL_BUTTON:
        return

    converted_id = message.id * abs(client.db_channel.id)
    string = f"get-{converted_id}"
    base64_string = await encode(string)
    link = f"https://t.me/{client.username}?start={base64_string}"
    
    # Generate short URL
    short_url = url_shortener.shorten_url(link)
    
    # Create inline keyboard with multiple buttons
    buttons = [
        [
            InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}'),
            InlineKeyboardButton("🔗 Short URL", url=short_url) if short_url else None
        ]
    ]
    # Remove None values from buttons
    buttons = [list(filter(None, row)) for row in buttons]
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    try:
        await message.edit_reply_markup(reply_markup)
    except Exception as e:
        print(e)
        pass
