import discord
from discord.ext import commands
from discord.ui import Button, View

intents = discord.Intents.default()
client = commands.Bot(command_prefix="!", intents=intents)

class GalleryViewer(View):
    def __init__(self, images):
        super().__init__(timeout=None)  # Keep the view alive indefinitely
        self.images = images
        self.current_image_index = 0

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.primary)
    async def previous(self, button: Button, interaction: discord.Interaction):
        self.current_image_index = (self.current_image_index - 1) % len(self.images)
        await self.update_image(interaction)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary)
    async def next(self, button: Button, interaction: discord.Interaction):
        self.current_image_index = (self.current_image_index + 1) % len(self.images)
        await self.update_image(interaction)

    async def update_image(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Gallery Viewer")
        embed.set_image(url=self.images[self.current_image_index])
        await interaction.response.edit_message(embed=embed, view=self)

@client.slash_command(name="gallery", description="View the image gallery")
async def gallery(interaction: discord.Interaction):
    images = [
        "url_to_image_1",  # Replace these with actual image URLs
        "url_to_image_2",
        "url_to_image_3",
        "url_to_image_4",
    ]
    view = GalleryViewer(images)

    embed = discord.Embed(title="Gallery Viewer")
    embed.set_image(url=images[0])
    await interaction.response.send_message(embed=embed, view=view)

client.run('YOUR_BOT_TOKEN')  # Add your bot token here