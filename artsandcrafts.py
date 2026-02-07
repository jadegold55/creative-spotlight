# Discord and UI imports
import discord
from discord import app_commands
from discord.ui import Button, View
import os

# For loading environment variables
from dotenv import load_dotenv

# Import the in-memory gallery image store
from gallery_data import gallery_images


# Set up Discord client and command tree
intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


# View class for gallery navigation and voting
class GalleryViewer(View):
    def __init__(self, images, user_id=None):
        super().__init__(timeout=None)
        self.images = images  # List of image dicts
        self.current_image_index = 0  # Track which image is shown
        self.user_id = user_id  # Optionally track the user viewing

    # Button to go to the previous image
    @discord.ui.button(label="Previous", style=discord.ButtonStyle.primary)
    async def previous(self, interaction: discord.Interaction, button: Button):
        self.current_image_index = (self.current_image_index - 1) % len(self.images)
        await self.update_image(interaction)

    # Button to go to the next image
    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary)
    async def next(self, interaction: discord.Interaction, button: Button):
        self.current_image_index = (self.current_image_index + 1) % len(self.images)
        await self.update_image(interaction)

    # Button to vote for the current image
    @discord.ui.button(label="Love it! ❤️", style=discord.ButtonStyle.success)
    async def love(self, interaction: discord.Interaction, button: Button):
        idx = self.current_image_index
        image = self.images[idx]
        user_id = interaction.user.id
        if user_id in image["votes"]:
            await interaction.response.send_message(
                "You already voted for this image!", ephemeral=True
            )
        else:
            image["votes"].add(user_id)
            await interaction.response.send_message(
                "You voted for this image! ❤️", ephemeral=True
            )
            await self.update_image(interaction, edit_only=True)

    # Helper to update the embed and view for the current image
    async def update_image(self, interaction: discord.Interaction, edit_only=False):
        image = self.images[self.current_image_index]
        embed = discord.Embed(title="Gallery Viewer")
        embed.set_image(url=image["url"])
        embed.set_footer(text=f"Votes: {len(image['votes'])}")
        if edit_only:
            await interaction.edit_original_response(embed=embed, view=self)
        else:
            await interaction.response.edit_message(embed=embed, view=self)


# Slash command to view the image gallery
@tree.command(name="gallery", description="View the image gallery")
async def gallery(interaction: discord.Interaction):
    import logging

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("gallery_command")
    logger.info(f"gallery command invoked by user {interaction.user.id}")
    try:
        await interaction.response.defer(thinking=True)
    except Exception as e:
        logger.error(f"Error deferring interaction: {e}")
        try:
            await interaction.followup.send(
                f"Error deferring interaction: {e}", ephemeral=True
            )
        except Exception as e2:
            logger.error(f"Error sending followup after defer failure: {e2}")
        return
    if not gallery_images:
        # Add some default images if empty
        gallery_images.extend(
            [
                {
                    "url": "https://images.unsplash.com/photo-1506744038136-46273834b3fb",
                    "uploader": None,
                    "votes": set(),
                },
                {
                    "url": "https://images.unsplash.com/photo-1465101046530-73398c7f28ca",
                    "uploader": None,
                    "votes": set(),
                },
                {
                    "url": "https://images.unsplash.com/photo-1519125323398-675f0ddb6308",
                    "uploader": None,
                    "votes": set(),
                },
                {
                    "url": "https://images.unsplash.com/photo-1529626455594-4ff0802cfb7e",
                    "uploader": None,
                    "votes": set(),
                },
            ]
        )
    view = GalleryViewer(gallery_images, user_id=interaction.user.id)
    embed = discord.Embed(title="Gallery Viewer")
    embed.set_image(url=gallery_images[0]["url"])
    embed.set_footer(text=f"Votes: {len(gallery_images[0]['votes'])}")
    try:
        await interaction.followup.send(embed=embed, view=view, ephemeral=False)
        logger.info("Sent gallery embed and view successfully.")
    except Exception as e:
        logger.error(f"Error sending gallery embed: {e}")
        try:
            await interaction.followup.send(
                f"Error sending gallery embed: {e}", ephemeral=True
            )
        except Exception as e2:
            logger.error(f"Error sending followup after embed failure: {e2}")


# Slash command to upload a new image to the gallery
@tree.command(name="upload", description="Upload an image to the gallery")
@app_commands.describe(image="Paste an image URL", file="Attach an image file")
async def upload(
    interaction: discord.Interaction, image: str = None, file: discord.Attachment = None
):
    await interaction.response.defer(thinking=True, ephemeral=True)
    url = None
    if image and (image.startswith("http://") or image.startswith("https://")):
        url = image
    elif file and file.content_type and file.content_type.startswith("image"):
        url = file.url
    if not url:
        await interaction.followup.send(
            "Please provide a valid image URL or attach an image file.", ephemeral=True
        )
        return
    gallery_images.append({"url": url, "uploader": interaction.user.id, "votes": set()})
    await interaction.followup.send(
        "Your image has been added to the gallery!", ephemeral=True
    )


# Load token from .env file
load_dotenv()
TOKEN = os.getenv("TOKEN")


# Event: Bot is ready and syncs slash commands (force sync to specific guild for instant registration)
@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    # Read guild ID from environment variable
    GUILD_ID = int(os.getenv("GUILD_ID"))
    guild = discord.Object(id=GUILD_ID)
    await tree.sync(guild=guild)
    print(f"Slash commands synced to guild {GUILD_ID}")


# Start the Discord bot
client.run(TOKEN)
