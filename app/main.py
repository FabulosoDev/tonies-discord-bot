import os
import discord
from dotenv import load_dotenv
from tonies_api import ToniesApi
from tonies_json import ToniesJson
from flipper_nfc import FlipperNfc
from discord_embed import DiscordEmbed
from logger_factory import DefaultLoggerFactory
from discord_reply import DiscordReply

logger = DefaultLoggerFactory.get_logger(__name__)

load_dotenv()

tonies_api = ToniesApi()
tonies_json = ToniesJson()

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    logger.info(f'Discord bot logged in as {client.user}')
    tonies_json.start_updates()

@client.event
async def on_message(message):
    # Handle commands in replies first
    if await DiscordReply.handle_command(message, client):
        return

    if f"{message.author}" != os.getenv('DISCORD_AUTHOR'):
        return

    # Handle NFC file processing
    if not message.attachments:
        logger.debug("Message has no attachments, ignoring")
        return

    attachment = message.attachments[0]
    if not attachment.filename.lower().endswith('.nfc'):
        logger.debug(f"Ignoring non-NFC file: {attachment.filename}")
        return

    logger.info(f"Processing NFC file: {attachment.filename}")
    nfc_content = await attachment.read()
    nfc_text = nfc_content.decode('utf-8')

    nfc = FlipperNfc(nfc_text)
    if not nfc.is_valid():
        logger.error("Could not find UID or Data Content in the NFC file")
        return

    if nfc.is_custom_tag():
        logger.warning(f"Ignoring custom tag with RUID: {nfc.ruid}")
        return

    logger.debug(f"Valid NFC data found - RUID: {nfc.ruid}, Auth: {nfc.auth}")
    result = await tonies_api.get_audio_id_and_hash(nfc.ruid, nfc.auth)
    if "audio_id" in result and "hash" in result:
        tonie = tonies_json.find_by_audio_id(result["audio_id"], result["hash"])
        tonie["ruid"] = nfc.ruid
        tonie["auth"] = nfc.auth
        if tonie:
            embed = DiscordEmbed.create_tonie_embed(tonie, attachment)
            await message.channel.send(embed=embed)
            logger.info("Sent embed message to Discord channel")
            await message.delete()
            logger.debug("Deleted original message")
        else:
            tonie = {"ruid": nfc.ruid, "auth": nfc.auth, "audio_id": result["audio_id"], "hash": result["hash"]}
            embed = DiscordEmbed.create_tonie_embed(tonie, attachment)
            await message.channel.send(embed=embed)
            logger.info("Sent embed message to Discord channel")
    else:
        logger.error(f"Error getting audio_id: {result}")
        await message.channel.send(str(result))

client.run(os.getenv('DISCORD_TOKEN'))