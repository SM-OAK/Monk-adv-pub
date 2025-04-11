# plugins/logger.py - Compatible with monk bot structure
from pyrogram import Client, filters
from pyrogram.types import Message
import traceback
from datetime import datetime

# List of admin user IDs who can use admin commands
ADMIN_USERS = [12345]  # Replace with actual admin user IDs

@Client.on_message(filters.command("logstatus") & filters.private)
async def log_status(client: Client, message: Message):
    """Command to log bot status"""
    user_id = message.from_user.id
    
    # Check if user is admin
    if user_id not in ADMIN_USERS:
        await message.reply_text("You don't have permission to use this command.")
        return
    
    try:
        uptime = datetime.now() - client.uptime
        hours, remainder = divmod(uptime.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        uptime_str = f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
        
        status_text = (
            f"✅ Bot is running\n"
            f"👤 Username: @{client.username}\n"
            f"⏱ Uptime: {uptime_str}\n"
            f"📅 Started: {client.uptime.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        await message.reply_text(status_text)
        
        # Log to channel if available
        if hasattr(client, 'log_to_channel'):
            await client.log_to_channel(f"#STATUS_CHECK:\n\nRequested by {message.from_user.mention}\n\n{status_text}")
            
    except Exception as e:
        error_text = f"Error checking status: {str(e)}"
        await message.reply_text(error_text)
        client.LOGGER(__name__).error(f"{error_text}\n{traceback.format_exc()}")

@Client.on_message(filters.command("sendlog") & filters.private)
async def send_log(client: Client, message: Message):
    """Command to manually send a log entry"""
    user_id = message.from_user.id
    
    # Check if user is admin
    if user_id not in ADMIN_USERS:
        await message.reply_text("You don't have permission to use this command.")
        return
    
    # Check if there's a message to log
    if len(message.text.split(" ", 1)) < 2:
        await message.reply_text("Please provide a message to log.\nExample: `/sendlog Test message`")
        return
    
    log_text = message.text.split(" ", 1)[1]
    
    try:
        # Log to channel if available
        if hasattr(client, 'log_to_channel'):
            await client.log_to_channel(f"#MANUAL_LOG:\n\n{log_text}")
            await message.reply_text("✅ Log message sent successfully.")
        else:
            await message.reply_text("❌ Logging to channel is not configured.")
    except Exception as e:
        error_text = f"Error sending log: {str(e)}"
        await message.reply_text(error_text)
        client.LOGGER(__name__).error(f"{error_text}\n{traceback.format_exc()}")

# Add this to any plugin file to log errors
def log_error(client, text, error=None):
    """Helper function to log errors"""
    client.LOGGER(__name__).error(text)
    if error:
        error_traceback = traceback.format_exc()
        client.LOGGER(__name__).error(error_traceback)
    
    # Try to send to log channel if available
    if hasattr(client, 'log_to_channel'):
        try:
            error_msg = f"#ERROR:\n\n{text}"
            if error:
                error_msg += f"\n\nDetails: {str(error)}\n```{error_traceback}```"
            client.loop.create_task(client.log_to_channel(error_msg))
        except:
            pass
