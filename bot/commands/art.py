import asyncio
import logging
from io import BytesIO

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands

from bot.scraping.artsearch import scrapeArt

log = logging.getLogger(__name__)


class Art(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.command(name="art", description="Get a random piece of art")
    async def random_art(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True, ephemeral=True)

        art_data = await asyncio.to_thread(scrapeArt)
        if not art_data or not art_data.get("image_url"):
            await interaction.followup.send(
                "Sorry, I couldn't fetch a piece of art at the moment.",
                ephemeral=True,
            )
            return

        log.info(f"image_url: {art_data['image_url']}")

        async with aiohttp.ClientSession() as session:
            async with session.get(
                art_data["image_url"],
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (compatible; " "CreativitySpotlightBot/1.0)"
                    )
                },
            ) as res:
                log.info(f"IIIF download status: {res.status}")
                if res.status != 200:
                    await interaction.followup.send(
                        "Couldn't download the art image.",
                        ephemeral=True,
                    )
                    return
                image_bytes = await res.read()

        image_file = discord.File(BytesIO(image_bytes), filename="artwork.jpg")
        art_embed = discord.Embed(
            title=art_data["title"],
            description=(f"By {art_data['artist']}\n\n" f"{art_data['date']}"),
            color=discord.Color.purple(),
        )
        await interaction.followup.send(
            file=image_file, embed=art_embed, ephemeral=True
        )


async def setup(bot):
    await bot.add_cog(Art(bot))
