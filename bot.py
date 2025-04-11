#(©)Codexbotz

from aiohttp import web
from plugins import web_server

import pyromod.listen
from pyrogram import Client
from pyrogram.enums import ParseMode
import sys
import traceback
from datetime import datetime

from config import API_HASH, APP_ID, LOGGER, TG_BOT_TOKEN, TG_BOT_WORKERS, FORCE_SUB_CHANNEL, CHANNEL_ID, PORT, LOG_CHANNEL

class Bot(Client):
    def __init__(self):
        super().__init__(
            name="Bot",
            api_hash=API_HASH,
            api_id=APP_ID,
            plugins={
                "root": "plugins"
            },
            workers=TG_BOT_WORKERS,
            bot_token=TG_BOT_TOKEN
        )
        self.LOGGER = LOGGER

    async def log_to_channel(self, text):
        """Send log messages to the configured log channel"""
        if LOG_CHANNEL:
            try:
                await self.send_message(LOG_CHANNEL, f"#LOG:\n\n{text}")
            except Exception as e:
                self.LOGGER(__name__).error(f"Failed to send log to channel: {e}")
                print(f"Failed to send log to channel: {e}")

    async def start(self):
        await super().start()
        usr_bot_me = await self.get_me()
        self.uptime = datetime.now()

        # Log bot startup
        startup_text = f"Bot started successfully!\nBot Username: @{usr_bot_me.username}\nStartup Time: {self.uptime.strftime('%Y-%m-%d %H:%M:%S')}"
        await self.log_to_channel(startup_text)

        if FORCE_SUB_CHANNEL:
            try:
                link = (await self.get_chat(FORCE_SUB_CHANNEL)).invite_link
                if not link:
                    await self.export_chat_invite_link(FORCE_SUB_CHANNEL)
                    link = (await self.get_chat(FORCE_SUB_CHANNEL)).invite_link
                self.invitelink = link
                await self.log_to_channel(f"Force Sub Channel link generated: {link}")
            except Exception as a:
                error_text = f"Force Sub Channel Error: {a}\nPlease check FORCE_SUB_CHANNEL value: {FORCE_SUB_CHANNEL}"
                await self.log_to_channel(f"#ERROR:\n\n{error_text}\n\n**Traceback:** `{traceback.format_exc()}`")
                self.LOGGER(__name__).warning(a)
                self.LOGGER(__name__).warning("Bot can't Export Invite link from Force Sub Channel!")
                self.LOGGER(__name__).warning(f"Please Double check the FORCE_SUB_CHANNEL value and Make sure Bot is Admin in channel with Invite Users via Link Permission, Current Force Sub Channel Value: {FORCE_SUB_CHANNEL}")
                self.LOGGER(__name__).info("\nBot Stopped. Join https://t.me/CodeXBotzSupport for support")
                sys.exit()
        try:
            db_channel = await self.get_chat(CHANNEL_ID)
            self.db_channel = db_channel
            test = await self.send_message(chat_id = db_channel.id, text = "Test Message")
            await test.delete()
            await self.log_to_channel(f"Successfully connected to DB Channel: {db_channel.title}")
        except Exception as e:
            error_text = f"DB Channel Error: {e}\nPlease check CHANNEL_ID value: {CHANNEL_ID}"
            await self.log_to_channel(f"#ERROR:\n\n{error_text}\n\n**Traceback:** `{traceback.format_exc()}`")
            self.LOGGER(__name__).warning(e)
            self.LOGGER(__name__).warning(f"Make Sure bot is Admin in DB Channel, and Double check the CHANNEL_ID Value, Current Value {CHANNEL_ID}")
            self.LOGGER(__name__).info("\nBot Stopped. Join https://t.me/ultroidofficial_Support for support")
            sys.exit()

        self.set_parse_mode(ParseMode.HTML)
        self.LOGGER(__name__).info(f"Bot Running..!\n\nCreated by \nhttps://t.me/ultroidofficial")
        self.LOGGER(__name__).info(f""" \n\n       
(っ◔◡◔)っ ♥ ULTROIDOFFICIAL ♥
░╚════╝░░╚════╝░╚═════╝░╚══════╝
                                          """)
        self.username = usr_bot_me.username
        #web-response
        app = web.AppRunner(await web_server())
        await app.setup()
        bind_address = "0.0.0.0"
        await web.TCPSite(app, bind_address, PORT).start()
        await self.log_to_channel(f"Web server started on port {PORT}")

    async def stop(self, *args):
        uptime_duration = datetime.now() - self.uptime
        hours, remainder = divmod(uptime_duration.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        uptime_text = f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
        
        await self.log_to_channel(f"Bot stopped.\nTotal uptime: {uptime_text}")
        await super().stop()
        self.LOGGER(__name__).info("Bot stopped.")

    async def handle_error(self, func_name, error, additional_info=None):
        """Handle and log errors properly"""
        error_text = f"Error in {func_name}: {error}"
        if additional_info:
            error_text += f"\nAdditional Info: {additional_info}"
        
        error_text += f"\n\n**Traceback:** `{traceback.format_exc()}`"
        await self.log_to_channel(f"#ERROR_TRACEBACK:\n\n{error_text}")
        self.LOGGER(__name__).error(error_text)
        print(error_text)
