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

@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command('batch'))
async def batch(client: Client, message: Message):
    while True:
        try:
            first_message = await client.ask(text = "Forward the First Message from DB Channel (with Quotes)..\n\nor Send the DB Channel Post Link", chat_id = message.from_user.id, filters=(filters.forwarded | (filters.text & ~filters.forwarded)), timeout=60)
        except:
            return
        f_msg_id = await get_message_id(client, first_message)
        if f_msg_id:
            break
        else:
            await first_message.reply("❌ Error\n\nthis Forwarded Post is not from my DB Channel or this Link is taken from DB Channel", quote = True)
            continue

    while True:
        try:
            second_message = await client.ask(text = "Forward the Last Message from DB Channel (with Quotes)..\nor Send the DB Channel Post link", chat_id = message.from_user.id, filters=(filters.forwarded | (filters.text & ~filters.forwarded)), timeout=60)
        except:
            return
        s_msg_id = await get_message_id(client, second_message)
        if s_msg_id:
            break
        else:
            await second_message.reply("❌ Error\n\nthis Forwarded Post is not from my DB Channel or this Link is taken from DB Channel", quote = True)
            continue

    string = f"get-{f_msg_id * abs(client.db_channel.id)}-{s_msg_id * abs(client.db_channel.id)}"
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
    await second_message.reply_text(
        f"<b>Here is your link</b>\n\n{link}\n\n<b>Short URL:</b> {short_url or 'Unable to generate'}", 
        quote=True, 
        reply_markup=reply_markup
    )


@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command('genlink'))
async def link_generator(client: Client, message: Message):
    while True:
        try:
            channel_message = await client.ask(text = "Forward Message from the DB Channel (with Quotes)..\nor Send the DB Channel Post link", chat_id = message.from_user.id, filters=(filters.forwarded | (filters.text & ~filters.forwarded)), timeout=60)
        except:
            return
        msg_id = await get_message_id(client, channel_message)
        if msg_id:
            break
        else:
            await channel_message.reply("❌ Error\n\nthis Forwarded Post is not from my DB Channel or this Link is not taken from DB Channel", quote = True)
            continue

    base64_string = await encode(f"get-{msg_id * abs(client.db_channel.id)}")
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
    await channel_message.reply_text(
        f"<b>Here is your link</b>\n\n{link}\n\n<b>Short URL:</b> {short_url or 'Unable to generate'}", 
        quote=True, 
        reply_markup=reply_markup
    )
