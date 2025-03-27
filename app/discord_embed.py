from datetime import datetime, timezone
import discord
from logger_factory import DefaultLoggerFactory

logger = DefaultLoggerFactory.get_logger(__name__)

class DiscordEmbed:
    @staticmethod
    def create_tonie_embed(tonie_data: dict, attachment: discord.Attachment) -> discord.Embed:
        """Create a Discord embed message from tonie data"""
        embed = discord.Embed(
            title=tonie_data.get("episode", "No episode available"),
            description=tonie_data.get('series', 'No series available'),
            url=tonie_data.get("web", None),
        )

        embed.set_author(name=attachment.filename, url=attachment.url)
        
        if tonie_data["age"] is not None:
            embed.add_field(name="Age", value=f"{tonie_data['age']} years", inline=True)

        if tonie_data["language"] is not None:
            embed.add_field(name="Language", value=tonie_data["language"], inline=True)

        if tonie_data["runtime"] is not None:
            embed.add_field(name="Runtime", value=f"{tonie_data['runtime']} min", inline=True)

        if tonie_data["tracks"] is not None:
            embed.add_field(name="Tracks", value=str(tonie_data["tracks"]), inline=True)          

        if tonie_data["track_desc"]:
            tracks_list = "\n".join(f"{i+1}. {track}" for i, track in enumerate(tonie_data["track_desc"]))
            embed.add_field(name="Tracklist", value=tracks_list, inline=False)

        if "image" in tonie_data:
            embed.set_thumbnail(url=tonie_data["image"])

        if "release" in tonie_data:
            try:
                release_date = datetime.fromtimestamp(int(tonie_data["release"]), tz=timezone.utc)
                formatted_date = release_date.strftime("%Y-%m-%d")
                embed.set_footer(text=f"Released: {formatted_date}")
            except (ValueError, TypeError) as e:
                logger.error(f"Error converting timestamp: {e}")
                
        return embed