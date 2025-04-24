#(©)Codexbotz

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from bot import Bot
from config import ADMINS
from helper_func import encode, get_message_id
import requests

class CustomUrlShortener:
    def __init__(self, api_key=None, domain='shrinkforearn.in'):
        """
        Initialize custom URL shortener 
        
        Args:
            api_key (str, optional): API key for the URL shortening service
            domain (str, optional): Domain to use for shortening (default: shrinkforearn.in)
        """
        self.api_key = api_key
        self.domain = domain
    
    def shorten_url(self, long_url):
        """
        Generate a short URL using ShrinkEarn/ShrinkMe API
        
        Args:
            long_url (str): The long URL to be shortened
        
        Returns:
            str or None: Shortened URL or None if unsuccessful
        """
        try:
            # ShrinkMe API endpoint
            api_url = f"https://shrinkforearn.in/api"
            
            # Prepare parameters
            params = {
                'api': self.api_key,
                'url': long_url,
                'format': 'text'  # Plain text response
            }
            
            # Send request
            response = requests.get(api_url, params=params, timeout=10)
            
            # Check if request was successful
            if response.status_code == 200 and response.text.startswith('http'):
                return response.text.strip()
            
            # Log error if something went wrong
            print(f"URL Shortening Error: {response.text}")
            return None
        
        except requests.RequestException as e:
            print(f"Error generating short URL: {e}")
            return None

# Initialize the shortener (you'll want to add your API key in config.py)
from config import URL_SHORTENER_API_KEY

url_shortener = CustomUrlShortener(api_key=URL_SHORTENER_API_KEY)

def has_single_file(message: Message) -> bool:
    """
    Check if a message contains exactly one file (document, photo, video, or audio).
    
    Args:
        message (Message): The message to check
        
    Returns:
        bool: True if the message has exactly one file, False otherwise
    """
    file_types = [
        message.document,
        message.photo,
        message.video,
        message.audio
    ]
    files = [f for f in file_types if f is not None]
    return len(files) == 1

@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command('batch'))
async def batch(client: Client, message: Message):
    while True:
        try:
            first_message = await client.ask(
                text="Forward the First Message from DB Channel (with Quotes, must contain exactly one file)..\n\nor Send the DB Channel Post Link",
                chat_id=message.from_user.id,
                filters=(filters.forwarded | (filters.text & ~filters.forwarded)),
                timeout=60
            )
        except:
            await message.reply("❌ Batch command timed out or failed.")
            return
        
        # Validate the first message
        f_msg_id = await get_message_id(client, first_message)
        if not f_msg_id:
            await first_message.reply(
                "❌ Error\n\nThis forwarded post is not from my DB Channel or the link is invalid.",
                quote=True
            )
            continue
        
        # Check if the message has exactly one file
        if not first_message.forward_from_chat or not has_single_file(first_message):
            await first_message.reply(
                "❌ Error\n\nThe forwarded message must contain exactly one file (e.g., one document, photo, video, or audio).",
                quote=True
            )
            continue
        break

    while True:
        try:
            second_message = await client.ask(
                text="Forward the Last Message from DB Channel (with Quotes, must contain exactly one file)..\nor Send the DB Channel Post Link",
                chat_id=message.from_user.id,
                filters=(filters.forwarded | (filters.text & ~filters.forwarded)),
                timeout=60
            )
        except:
            await message.reply("❌ Batch command timed out or failed.")
            return
        
        # Validate the second message
        s_msg_id = await get_message_id(client, second_message)
        if not s_msg_id:
            await second_message.reply(
                "❌ Error\n\nThis forwarded post is not from my DB Channel or the link is invalid.",
                quote=True
            )
            continue
        
        # Check if the message has exactly one file
        if not second_message.forward_from_chat or not has_single_file(second_message):
            await second_message.reply(
                "❌ Error\n\nThe forwarded message must contain exactly one file (e.g., one document, photo, video, or audio).",
                quote=True
            )
            continue
        
        # Ensure the range is valid (first_message_id <= last_message_id)
        if s_msg_id < f_msg_id:
            await second_message.reply(
                "❌ Error\n\nThe last message ID must be greater than or equal to the first message ID.",
                quote=True
            )
            continue
        break

    # Generate the batch link
    string = f"get-{f_msg_id * abs(client.db_channel.id)}-{s_msg_id * abs(client.db_channel.id)}"
    base64_string = await encode(string)
    link = f"https://t.me/{client.username}?start={base64_string}"
    
    # Generate short URL
    short_url = url_shortener.shorten_url(link) or "Unable to generate short URL"
    
    # Create inline keyboard with multiple buttons
    buttons = [
        [
            InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}'),
            InlineKeyboardButton("🔗 Short URL", url=short_url) if short_url != "Unable to generate short URL" else None
        ]
    ]
    # Remove None values from buttons
    buttons = [list(filter(None, row)) for row in buttons]
    
    reply_markup = InlineKeyboardMarkup(buttons)
    await second_message.reply_text(
        f"<b>Batch link generated successfully!</b>\n\n"
        f"<b>Link:</b> {link}\n"
        f"<b>Short URL:</b> {short_url}\n\n"
        f"This link includes messages {f_msg_id} to {s_msg_id}, each with one file.",
        quote=True,
        reply_markup=reply_markup
    )

@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command('genlink'))
async def link_generator(client: Client, message: Message):
    while True:
        try:
            channel_message = await client.ask(
                text="Forward Message from the DB Channel (with Quotes, must contain exactly one file)..\nor Send the DB Channel Post Link",
                chat_id=message.from_user.id,
                filters=(filters.forwarded | (filters.text & ~filters.forwarded)),
                timeout=60
            )
        except:
            await message.reply("❌ Genlink command timed out or failed.")
            return
        
        # Validate the message
        msg_id = await get_message_id(client, channel_message)
        if not msg_id:
            await channel_message.reply(
                "❌ Error\n\nThis forwarded post is not from my DB Channel or the link is invalid.",
                quote=True
            )
            continue
        
        # Check if the message has exactly one file
        if not channel_message.forward_from_chat or not has_single_file(channel_message):
            await channel_message.reply(
                "❌ Error\n\nThe forwarded message must contain exactly one file (e.g., one document, photo, video, or audio).",
                quote=True
            )
            continue
        break

    # Generate the single message link
    base64_string = await encode(f"get-{msg_id * abs(client.db_channel.id)}")
    link = f"https://t.me/{client.username}?start={base64_string}"
    
    # Generate short URL
    short_url = url_shortener.shorten_url(link) or "Unable to generate short URL"
    
    # Create inline keyboard with multiple buttons
    buttons = [
        [
            InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}'),
            InlineKeyboardButton("🔗 Short URL", url=short_url) if short_url != "Unable to generate short URL" else None
        ]
    ]
    # Remove None values from buttons
    buttons = [list(filter(None, row)) for row in buttons]
    
    reply_markup = InlineKeyboardMarkup(buttons)
    await channel_message.reply_text(
        f"<b>Single file link generated successfully!</b>\n\n"
        f"<b>Link:</b> {link}\n"
        f"<b>Short URL:</b> {short_url}",
        quote=True,
        reply_markup=reply_markup
    )
