# Discord and UI imports
import logging
import aiohttp
import discord
from discord import app_commands
from discord import file
from discord.ui import Button, View

from discord.ext import commands
import requests
from bot.apihelper.api import post, get

from bot.config import PUBLIC_URL


# Set up Discord client and command tree

# functionality to add:  find database of art pieces and artists,
# scrape for images and info, add to database, then create commands to pull from the
# database and display in discord. I can also add a command to allow users to submit their own art
# pieces to the gallery, which would be a fun way to engage the community and keep the gallery fresh with new content.
#  I will need to add some error handling and logging to make sure it runs smoothly, especially if i want to run it on a schedule.


# view ui for gallery
class GalleryViewer(View):
    def __init__(self, images, user_id=None):
        super().__init__(timeout=None)
        self.images = images  # List of image dicts
        self.current_image_index = 0  # Track which image is shown
        self.user_id = user_id
        if len(images) <= 1:
            self.previous.disabled = True
            self.next.disabled = True  # Optionally track the user viewing

    # go to previous pic
    @discord.ui.button(label="Previous", style=discord.ButtonStyle.primary)
    async def previous(self, interaction: discord.Interaction, button: Button):
        self.current_image_index = (self.current_image_index - 1) % len(self.images)
        await self.update_image(interaction)

    # next pic
    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary)
    async def next(self, interaction: discord.Interaction, button: Button):
        self.current_image_index = (self.current_image_index + 1) % len(self.images)
        await self.update_image(interaction)

    # do u like the image or not
    @discord.ui.button(label="❤️", style=discord.ButtonStyle.success)
    async def love(self, interaction: discord.Interaction, button: Button):
        idx = self.current_image_index
        image = self.images[idx]
        user_id = interaction.user.id

        status, response = await post(
            f"images/{image['id']}/vote",
            params={"userID": user_id},
        )
        if status == 409:
            await interaction.response.send_message(
                "You've already voted for this image!", ephemeral=True
            )
            return
        await interaction.response.send_message("Thanks for voting!", ephemeral=True)
        vote_count = await get(f"images/{image['id']}/votes")
        await self.update_image(interaction, edit_only=True, vote_count=vote_count)

    async def update_image(
        self, interaction: discord.Interaction, edit_only=False, vote_count=None
    ):
        image = self.images[self.current_image_index]
        if vote_count is None:
            vote_count = await get(f"images/{image['id']}/votes")
        embed = discord.Embed(title="Gallery Viewer")
        embed.set_image(url=f"{PUBLIC_URL}/images/{image['id']}/file")
        embed.set_footer(text=f"Votes: {vote_count if vote_count is not None else 0}")
        if edit_only:
            await interaction.edit_original_response(embed=embed, view=self)
        else:
            await interaction.response.edit_message(embed=embed, view=self)


class Gallery(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="gallery", description="View the image gallery")
    async def gallery(self, interaction: discord.Interaction):
        logger = logging.getLogger("gallery_command")
        await interaction.response.defer(thinking=True)
        images = await get(f"images/all", params={"guildid": interaction.guild.id})
        if not images:
            await interaction.followup.send(
                "The gallery is currently empty. Please check back later!",
                ephemeral=True,
            )
            return
        for img in images:
            img["votes"] = set()  # Convert votes to a set for easy management
        first_image = images[0]
        vote_count = await get(f"images/{first_image['id']}/votes")
        view = GalleryViewer(images, user_id=interaction.user.id)
        embed = discord.Embed(title="Gallery Viewer")
        embed.set_image(url=f"{PUBLIC_URL}/images/{first_image['id']}/file")
        embed.set_footer(text=f"Votes: {vote_count}")
        # time based event. invoked by bot iself every week.
        # users submit their images then the veent lasts like a weekend or something``

        try:
            await interaction.followup.send(embed=embed, view=view)
        except Exception as e:
            logger.error(f"Error sending gallery: {e}")

    @app_commands.command(name="upload", description="Upload an image to the gallery")
    @app_commands.describe(file="Attach an image file")
    async def upload(
        self,
        interaction: discord.Interaction,
        file: discord.Attachment = None,
    ):
        await interaction.response.defer(thinking=True, ephemeral=True)

        url = None
        if file and file.content_type and file.content_type.startswith("image"):
            url = file.url

        if not url:
            await interaction.followup.send(
                "Please provide a valid image URL or attachment.", ephemeral=True
            )
            return

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as res:
                image_bytes = await res.read()
        form = aiohttp.FormData()
        form.add_field(
            "file", image_bytes, filename=file.filename, content_type=file.content_type
        )
        form.add_field("uploaderid", str(interaction.user.id))
        form.add_field("guildid", str(interaction.guild.id))
        status, resp = await post(f"images/add", data=form)
        if status != 200:
            await interaction.followup.send(
                f"Failed to upload: {status}", ephemeral=True
            )
            return
        await interaction.followup.send(
            "Your image has been added to the gallery!", ephemeral=True
        )


# entry(Required for load_extension)
async def setup(bot):
    await bot.add_cog(Gallery(bot))
