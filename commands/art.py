# Discord and UI imports
import logging
import discord
from discord import app_commands
from discord.ui import Button, View
import os
from discord.ext import commands

# For loading environment variables
from dotenv import load_dotenv

# Import the in-memory gallery image store
from gallery_data import gallery_images


# Set up Discord client and command tree




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
    @discord.ui.button(label="❤️", style=discord.ButtonStyle.success)
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
                "Thanks for voting!", ephemeral=True
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
class Gallery(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # 3. Use @app_commands.command instead of @tree.command
    @app_commands.command(name="gallery", description="View the image gallery")
    async def gallery(self, interaction: discord.Interaction):
        # Initialize Logging locally for this command
        logger = logging.getLogger("gallery_command")
        
        # Defer immediately to prevent timeout
        await interaction.response.defer(thinking=True)

        if not gallery_images:
            # Add default images if empty
            gallery_images.extend([
                {"url": "https://images.unsplash.com/photo-1506744038136-46273834b3fb", "votes": set()},
                {"url": "https://images.unsplash.com/photo-1465101046530-73398c7f28ca", "votes": set()},
            ])

        view = GalleryViewer(gallery_images, user_id=interaction.user.id)
        embed = discord.Embed(title="Gallery Viewer")
        embed.set_image(url=gallery_images[0]["url"])
        embed.set_footer(text=f"Votes: {len(gallery_images[0]['votes'])}")

        try:
            await interaction.followup.send(embed=embed, view=view)
        except Exception as e:
            logger.error(f"Error sending gallery: {e}")

    @app_commands.command(name="upload", description="Upload an image to the gallery")
    @app_commands.describe(image="Paste an image URL", file="Attach an image file")
    async def upload(self, interaction: discord.Interaction, image: str = None, file: discord.Attachment = None):
        await interaction.response.defer(thinking=True, ephemeral=True)
        
        url = None
        if image and (image.startswith("http://") or image.startswith("https://")):
            url = image
        elif file and file.content_type and file.content_type.startswith("image"):
            url = file.url
            
        if not url:
            await interaction.followup.send("Please provide a valid image URL or attachment.", ephemeral=True)
            return
            
        gallery_images.append({"url": url, "uploader": interaction.user.id, "votes": set()})
        await interaction.followup.send("Your image has been added to the gallery!", ephemeral=True)

# 4. The Setup Entry Point (Required for load_extension)
async def setup(bot):
    await bot.add_cog(Gallery(bot))