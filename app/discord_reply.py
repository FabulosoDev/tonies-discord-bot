import urllib.parse
import discord
from logger_factory import DefaultLoggerFactory

logger = DefaultLoggerFactory.get_logger(__name__)

class DiscordReply:
    CMD_PREFIX = "!"
    FAKE_DATA_URL = "https://tonies.local/data"

    @staticmethod
    def parse_hidden_data(url: str) -> dict:
        """Parse encoded data from URL"""
        if not url or not url.startswith(DiscordReply.FAKE_DATA_URL):
            return {}

        query = urllib.parse.urlparse(url).query
        return dict(urllib.parse.parse_qsl(query))

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

        tonie_data = DiscordReply.parse_hidden_data(embed.footer.icon_url)
        if not tonie_data:
            logger.warning("Could not parse data from URL")
            await message.reply("❌ Invalid data format")
            return

        name_or_ruid = embed.title if embed.title else f"rUID: {tonie_data.get('ruid')}"

        logger.info(f"Adding tonie: {name_or_ruid}")
        await message.reply(f"✅ Adding tonie: {name_or_ruid}")

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