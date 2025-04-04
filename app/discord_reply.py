import base64
import json
import urllib.parse
import discord
import asyncio
from logger_factory import DefaultLoggerFactory

logger = DefaultLoggerFactory.get_logger(__name__)

class DiscordReply:
    CMD_PREFIX = "!"
    FAKE_DATA_URL = "https://tonies.local"
    on_add_callback = None

    @staticmethod
    def on_add(func):
        """Decorator to register an external add callback."""
        if asyncio.iscoroutinefunction(func):
            DiscordReply.on_add_callback = func
            return func
        else:
            return None

    @staticmethod
    def parse_hidden_data_url(url: str) -> dict:
        """Parse base64 encoded JSON data from URL"""
        if not url or not url.startswith(DiscordReply.FAKE_DATA_URL):
            return {}

        try:
            # Extract base64 data from URL
            parsed = urllib.parse.urlparse(url)
            query = dict(urllib.parse.parse_qsl(parsed.query))
            encoded_data = query.get('data', '')

            # Decode base64 and parse JSON
            json_data = base64.urlsafe_b64decode(encoded_data).decode()
            return json.loads(json_data)
        except Exception as e:
            logger.error(f"Error decoding tonie data: {e}")
            return {}

    @staticmethod
    async def handle_add_command(message: discord.Message, referenced: discord.Message) -> None:
        """Handle the add command"""
        if not referenced.embeds:
            logger.warning("Referenced message has no embed")
            await message.reply("❌ This message doesn't contain tonie data")
            return

        embed = referenced.embeds[0]
        if not embed.footer or not embed.footer.icon_url:
            logger.warning("No data URL found in embed footer")
            await message.reply("❌ Could not find tonie data")
            return

        tonie_data = DiscordReply.parse_hidden_data_url(embed.footer.icon_url)
        if not tonie_data:
            logger.warning("Could not parse data from URL")
            await message.reply("❌ Invalid data format")
            return

        episode_or_ruid = tonie_data.get("episode") or f"rUID: {tonie_data.get('ruid')}"

        if DiscordReply.on_add_callback is not None:
            result = await DiscordReply.on_add_callback(tonie_data)
            if result.get("success", False):
                logger.info(f"Successfully added tonie: {episode_or_ruid}")
                await message.reply(f"✅ Successfully added tonie: {episode_or_ruid}")
            else:
                error = result.get("error", "Unknown error")
                logger.error(f"Failed to add tonie {episode_or_ruid}: {error}")
                await message.reply(f"❌ Failed to add tonie: {error}")
        else:
            logger.warning("No add callback registered")
            await message.reply("❌ Add functionality not available")

    @staticmethod
    async def get_referenced_message(message: discord.Message, client: discord.Client) -> discord.Message | None:
        """Get the referenced message if it exists and is from the bot"""
        if not message.reference:
            return None

        referenced = await message.channel.fetch_message(message.reference.message_id)
        if not referenced or referenced.author != client.user:
            logger.debug("Referenced message is not from bot or doesn't exist")
            return None

        return referenced

    @staticmethod
    async def handle_command(message: discord.Message, client: discord.Client) -> bool:
        """Handle commands in replies to bot messages"""
        if not message.content.startswith(DiscordReply.CMD_PREFIX):
            return False

        referenced = await DiscordReply.get_referenced_message(message, client)
        if not referenced:
            return False

        cmd = message.content[len(DiscordReply.CMD_PREFIX):].lower()
        logger.debug(f"Processing command: {cmd}")

        match cmd:
            case "add":
                await DiscordReply.handle_add_command(message, referenced)
            case _:
                logger.debug(f"Unknown command: {cmd}")
                return False

        return True