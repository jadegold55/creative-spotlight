from discord.ext import commands
from discord import app_commands
import discord
from io import BytesIO
import requests
from bot.scraping.artsearch import scrapeArt


class Art(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="art", description="Get a random piece of art")
    async def random_art(self, interaction: discord.Interaction):

        art_data = scrapeArt()
        print(f"image_url being sent: {art_data['image_url']}")
        if not art_data:
            await interaction.response.send_message(
                "Sorry, I couldn't fetch a piece of art at the moment."
            )
            return
        image_response = requests.get(art_data["image_url"])
        if image_response.status_code != 200:
            await interaction.response.send_message(
                "Sorry, I couldn't fetch the art image at the moment."
            )
            return
        image_file = discord.File(
            BytesIO(image_response.content), filename="artwork.jpg"
        )
        art_embed = discord.Embed(
            title=art_data["title"],
            description=f"By {art_data['artist']}\n\n{art_data['date']}",
            color=discord.Color.purple(),
        )
        art_embed.set_image(url=art_data["image_url"])
        print(f"embed image url: {art_embed.image.url}")
        await interaction.response.send_message(
            file=image_file, embed=art_embed, ephemeral=True
        )


async def setup(bot):
    await bot.add_cog(Art(bot))
