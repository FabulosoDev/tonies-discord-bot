from datetime import datetime, timezone
import discord

class DiscordEmbed:
    @staticmethod
    def create_tonie_embed(tonie_data: dict, url: str) -> discord.Embed:
        """Create a Discord embed message from tonie data"""
        embed = discord.Embed(
            title=tonie_data.get("episodes", "No episodes available"),
            description=tonie_data.get('series', 'No series available'),
            url=url
        )

        if "language" in tonie_data:
            embed.add_field(name="Language", value=tonie_data["language"], inline=True)

        if "category" in tonie_data:
            embed.add_field(name="Category", value=tonie_data["category"], inline=True)
        
        tracks = tonie_data.get("tracks", [])
        if tracks and len(tracks) > 0:
            tracks_text = "\n".join(f"{i+1}. {track}" for i, track in enumerate(tracks))
            embed.add_field(name=f"Tracks [{len(tracks)}]", value=tracks_text, inline=False)

        if "pic" in tonie_data:
            embed.set_thumbnail(url=tonie_data["pic"])

        if "release" in tonie_data:
            try:
                release_date = datetime.fromtimestamp(int(tonie_data["release"]), tz=timezone.utc)
                formatted_date = release_date.strftime("%Y-%m-%d")
                embed.set_footer(text=f"Released: {formatted_date}")
            except (ValueError, TypeError) as e:
                print(f"Error converting timestamp: {e}")
                
        return embed