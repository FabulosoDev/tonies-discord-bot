import base64
import json
from datetime import datetime, timezone
import discord
import urllib.parse
from logger_factory import DefaultLoggerFactory

logger = DefaultLoggerFactory.get_logger(__name__)

class DiscordEmbed:
    FAKE_DATA_URL = "https://tonies.local"

    @staticmethod
    def create_hidden_data_url(tonie_data: dict) -> str:
        """Create a URL with base64 encoded tonie data"""
        try:
            hidden_data = {
                "ruid": tonie_data.get("ruid"),
                "auth": tonie_data.get("auth")
            }

            if episode := tonie_data.get("episode"):
                hidden_data["episode"] = episode

            json_data = json.dumps(hidden_data)
            encoded_data = base64.urlsafe_b64encode(json_data.encode()).decode()
            return f"{DiscordEmbed.FAKE_DATA_URL}?data={encoded_data}"
        except Exception as e:
            logger.error(f"Error encoding tonie data: {e}")
            return None

    @staticmethod
    def create_tonie_embed(tonie_data: dict, attachment: discord.Attachment) -> discord.Embed:
        """Create a Discord embed message from tonie data"""
        embed = discord.Embed(
            color=0xd2000e,
            title=tonie_data.get("episode", None),
            description=tonie_data.get("series", None),
            url=tonie_data.get("web", None),
        )

        embed.set_author(name=attachment.filename, url=attachment.url)

        hidden_data_url = DiscordEmbed.create_hidden_data_url(tonie_data)

        if "age" in tonie_data and tonie_data["age"] is not None:
            embed.add_field(name="Age", value=f"{tonie_data['age']} years", inline=True)

        if "language" in tonie_data and tonie_data["language"] is not None:
            embed.add_field(name="Language", value=tonie_data["language"], inline=True)

        if "runtime" in tonie_data and tonie_data["runtime"] is not None:
            embed.add_field(name="Runtime", value=f"{tonie_data['runtime']} min", inline=True)

        if "tracks" in tonie_data and tonie_data["tracks"] is not None:
            embed.add_field(name="Tracks", value=str(tonie_data["tracks"]), inline=True)

        if "track_desc" in tonie_data and tonie_data["track_desc"]:
            tracks_list = "\n".join(f"{i+1}. {track}" for i, track in enumerate(tonie_data["track_desc"]))

            # Trim the list if it exceeds 1024 characters
            if len(tracks_list) > 1024:
                trimmed_tracks = []
                current_length = 0
                more_indicator = "\n...and more"  # Length of the indicator text
                max_length = 1024 - len(more_indicator)  # Adjust max length to include the indicator

                for i, track in enumerate(tonie_data["track_desc"]):
                    track_entry = f"{i+1}. {track}"
                    if current_length + len(track_entry) + 1 > max_length:  # +1 for newline
                        break
                    trimmed_tracks.append(track_entry)
                    current_length += len(track_entry) + 1

                tracks_list = "\n".join(trimmed_tracks) + more_indicator

            embed.add_field(name="Tracklist", value=tracks_list, inline=False)

        if "image" in tonie_data and tonie_data["image"] is not None:
            embed.set_thumbnail(url=tonie_data["image"])

        if "release" in tonie_data and tonie_data["release"] is not None:
            try:
                release_date = datetime.fromtimestamp(int(tonie_data["release"]), tz=timezone.utc)
                formatted_date = release_date.strftime("%Y-%m-%d")
                embed.set_footer(text=f"Released: {formatted_date}", icon_url=hidden_data_url)
            except (ValueError, TypeError) as e:
                logger.error(f"Error converting timestamp: {e}")
                embed.set_footer(text="Released: unknown", icon_url=hidden_data_url)
        else:
            embed.set_footer(text="Released: unknown", icon_url=hidden_data_url)

        return embed