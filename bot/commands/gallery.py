# Discord and UI imports
import logging
import aiohttp
import discord
from discord import app_commands
from discord import file
from discord.ui import Button, View

from discord.ext import commands
import requests
from bot.apihelper.api import delete, post, get

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

    # do u like the image or not
    @discord.ui.button(label="❤️", style=discord.ButtonStyle.success)
    async def love(self, interaction: discord.Interaction, button: Button):
        idx = self.current_image_index
        image = self.images[idx]
        user_id = interaction.user.id

        status, response = await post(
            f"images/{image['id']}/vote",
            params={"userID": user_id},
            headers={
                "X-User-Id": str(interaction.user.id),
                "X-User-Name": str(interaction.user.name),
            },
        )
        if status == 409:
            await interaction.response.send_message(
                "You've already voted for this image!", ephemeral=True
            )
            return
        await interaction.response.send_message("Thanks for voting!", ephemeral=True)
        image["voteCount"] = image.get("voteCount", 0) + 1
        await self.update_image(
            interaction, edit_only=True, vote_count=image["voteCount"]
        )

    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary)
    async def next(self, interaction: discord.Interaction, button: Button):
        self.current_image_index = (self.current_image_index + 1) % len(self.images)
        await self.update_image(interaction)

    async def update_image(
        self, interaction: discord.Interaction, edit_only=False, vote_count=None
    ):
        image = self.images[self.current_image_index]
        if vote_count is None:
            vote_count = image.get("voteCount", 0)
        embed = discord.Embed(
            title="Title", description=f"*{image.get('title') or 'Untitled'}*"
        )
        embed.set_image(url=f"{PUBLIC_URL}/images/{image['id']}/file")

        embed.set_footer(text=f"Votes: {vote_count if vote_count is not None else 0}")
        if edit_only:
            await interaction.edit_original_response(embed=embed, view=self)
        else:
            await interaction.response.edit_message(embed=embed, view=self)


class Gallery(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.command(name="gallery", description="View the image gallery")
    async def gallery(self, interaction: discord.Interaction):
        logger = logging.getLogger("gallery_command")
        await interaction.response.defer(thinking=True)
        images = await get(
            f"images/all",
            params={"guildid": interaction.guild.id},
            headers={
                "X-User-Id": str(interaction.user.id),
                "X-User-Name": str(interaction.user.name),
                "X-Command": "gallery",
            },
        )
        if not images:
            await interaction.followup.send(
                "The gallery is currently empty. Please check back later!",
                ephemeral=True,
            )
            return
        first_image = images[0]
        view = GalleryViewer(images, user_id=interaction.user.id)
        embed = discord.Embed(
            title="Title", description=f"*{first_image.get('title') or 'Untitled'}*"
        )
        embed.set_image(url=f"{PUBLIC_URL}/images/{first_image['id']}/file")
        embed.set_footer(text=f"Votes: {first_image.get('voteCount', 0)}")
        # time based event. invoked by bot iself every week.
        # users submit their images then the veent lasts like a weekend or something``

        try:
            await interaction.followup.send(embed=embed, view=view)
        except Exception as e:
            logger.error(f"Error sending gallery: {e}")

    @app_commands.checks.cooldown(1, 30.0, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.command(name="upload", description="Upload an image to the gallery")
    @app_commands.describe(file="Attach an image file", title="Title of your Art!")
    async def upload(
        self,
        interaction: discord.Interaction,
        title: str,
        file: discord.Attachment,
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
        form.add_field("title", title)
        status, resp = await post(
            f"images/add",
            headers={
                "X-User-Id": str(interaction.user.id),
                "X-User-Name": str(interaction.user.name),
                "X-Command": "upload",
            },
            data=form,
        )
        if status != 200:
            await interaction.followup.send(
                f"Failed to upload: {status}", ephemeral=True
            )
            return
        await interaction.followup.send(
            "Your image has been added to the gallery!", ephemeral=True
        )

    @app_commands.checks.cooldown(1, 30.0, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.command(name="delete", description="Delete an image from the gallery")
    async def delete(
        self,
        interaction: discord.Interaction,
    ):
        await interaction.response.defer(thinking=True, ephemeral=True)
        images = await get(
            f"images/user/{interaction.user.id}",
            params={"guildid": interaction.guild.id},
            headers={"X-User-Id": str(interaction.user.id)},
        )

        if not images:
            await interaction.followup.send(
                "You have no submissions to delete.", ephemeral=True
            )
            return

        options = [
            discord.SelectOption(
                label=img.get("title") or "Untitled", value=str(img["id"])
            )
            for img in images[:25]
        ]

        view = DeleteView(options)
        await interaction.followup.send(
            "Select a submission to delete:", view=view, ephemeral=True
        )


class DeleteView(View):
    def __init__(self, options):
        super().__init__(timeout=60)
        select = discord.ui.Select(placeholder="Choose a submission", options=options)
        select.callback = self.on_select
        self.add_item(select)

    async def on_select(self, interaction):
        image_id = interaction.data["values"][0]
        status, text = await delete(
            f"images/{image_id}",
            headers={"X-User-Id": str(interaction.user.id)},
        )

        if status != 200:
            await interaction.response.edit_message(
                content="Failed to delete.", view=None
            )
            return

        await interaction.response.edit_message(
            content="Submission deleted!", view=None
        )


# entry(Required for load_extension)
async def setup(bot):
    await bot.add_cog(Gallery(bot))
