# Discord and UI imports
import logging
from collections import OrderedDict

import aiohttp
import discord
from discord import app_commands
from discord.ui import Button, View, LayoutView

from discord.ext import commands
from bot.apihelper.api import delete, post, get

from bot.config import PUBLIC_URL


def group_images_into_posts(images):
    """Group a flat list of images by groupId into posts."""
    posts = OrderedDict()
    for img in images:
        gid = img.get("groupId") or str(
            img["id"]
        )  # fallback for images without groupId
        if gid not in posts:
            posts[gid] = []
        posts[gid].append(img)
    return list(posts.values())


# view ui for gallery — uses Components V2 MediaGallery for multi-image posts
class GalleryViewer(LayoutView):
    def __init__(self, posts, user_id=None):
        super().__init__(timeout=None)
        self.posts = posts  # List of posts; each post is a list of image dicts
        self.current_post_index = 0
        self.user_id = user_id
        self._build_components()

    def _build_components(self):
        """Rebuild view components for the current post."""
        self.clear_items()
        post_images = self.posts[self.current_post_index]
        title = post_images[0].get("title") or "Untitled"
        uploader_id = post_images[0].get("uploaderId")
        total_votes = sum(img.get("voteCount", 0) for img in post_images)

        # text header above the container
        mention = f"<@{uploader_id}>" if uploader_id else "Unknown"
        self.add_item(
            discord.ui.TextDisplay(
                content=(
                    f"**Title:** {title}\n"
                    f"**Made by:** {mention}\n"
                    f"**Votes:** {total_votes}"
                )
            )
        )

        # media gallery (works for 1 or more images)
        gallery_items = [
            discord.MediaGalleryItem(
                media=f"{PUBLIC_URL}/images/{img['id']}/file",
                description=img.get("title") or "",
            )
            for img in post_images
        ]
        gallery = discord.ui.MediaGallery(*gallery_items)

        # navigation and vote buttons in an action row
        nav_disabled = len(self.posts) <= 1

        prev_btn = Button(
            label="◀", style=discord.ButtonStyle.primary, disabled=nav_disabled
        )
        prev_btn.callback = self._on_previous

        vote_btn = Button(label="❤️", style=discord.ButtonStyle.success)
        vote_btn.callback = self._on_vote

        next_btn = Button(
            label="▶", style=discord.ButtonStyle.primary, disabled=nav_disabled
        )
        next_btn.callback = self._on_next

        row = discord.ui.ActionRow(prev_btn, vote_btn, next_btn)

        # container with gallery and buttons
        container = discord.ui.Container(
            gallery,
            row,
            accent_colour=discord.Colour.blurple(),
        )
        self.add_item(container)

    async def _on_previous(self, interaction: discord.Interaction):
        self.current_post_index = (self.current_post_index - 1) % len(self.posts)
        self._build_components()
        await interaction.response.edit_message(view=self)

    async def _on_next(self, interaction: discord.Interaction):
        self.current_post_index = (self.current_post_index + 1) % len(self.posts)
        self._build_components()
        await interaction.response.edit_message(view=self)

    async def _on_vote(self, interaction: discord.Interaction):
        post_images = self.posts[self.current_post_index]
        first_image = post_images[0]

        status, response = await post(
            f"images/{first_image['id']}/vote",
            params={"userID": interaction.user.id},
            headers={
                "X-User-Id": str(interaction.user.id),
                "X-User-Name": str(interaction.user.name),
            },
        )
        if status == 409:
            await interaction.response.send_message(
                "You've already voted for this post!", ephemeral=True
            )
            return

        await interaction.response.send_message("Thanks for voting!", ephemeral=True)
        first_image["voteCount"] = first_image.get("voteCount", 0) + 1
        self._build_components()
        await interaction.message.edit(view=self)


class Gallery(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.command(name="gallery", description="View the image gallery")
    async def gallery(self, interaction: discord.Interaction):
        logger = logging.getLogger("gallery_command")
        await interaction.response.defer(thinking=True, ephemeral=True)
        images = await get(
            "images/all",
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

        posts = group_images_into_posts(images)
        view = GalleryViewer(posts, user_id=interaction.user.id)

        try:
            await interaction.followup.send(
                view=view,
                ephemeral=True,
            )
        except Exception as e:
            logger.error(f"Error sending gallery: {e}")

    @app_commands.checks.cooldown(1, 30.0, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.command(name="upload", description="Upload image(s) to the gallery")
    @app_commands.describe(
        title="Title of your Art!",
        file="Attach an image file",
        file2="Optional second image",
        file3="Optional third image",
        file4="Optional fourth image",
    )
    async def upload(
        self,
        interaction: discord.Interaction,
        title: str,
        file: discord.Attachment,
        file2: discord.Attachment = None,
        file3: discord.Attachment = None,
        file4: discord.Attachment = None,
    ):
        await interaction.response.defer(thinking=True, ephemeral=True)

        attachments = [f for f in [file, file2, file3, file4] if f is not None]

        # validate all are images
        for att in attachments:
            if not att.content_type or not att.content_type.startswith("image"):
                await interaction.followup.send(
                    f"`{att.filename}` is not a valid image.", ephemeral=True
                )
                return

        headers = {
            "X-User-Id": str(interaction.user.id),
            "X-User-Name": str(interaction.user.name),
            "X-Command": "upload",
        }

        # download all attachments
        async with aiohttp.ClientSession() as session:
            file_data = []
            for att in attachments:
                async with session.get(att.url) as res:
                    file_data.append((await res.read(), att.filename, att.content_type))

        # build form and upload (single or multi)
        form = aiohttp.FormData()
        if len(file_data) == 1:
            img_bytes, filename, content_type = file_data[0]
            form.add_field(
                "file", img_bytes, filename=filename, content_type=content_type
            )
            endpoint = "images/add"
        else:
            for img_bytes, filename, content_type in file_data:
                form.add_field(
                    "files", img_bytes, filename=filename, content_type=content_type
                )
            endpoint = "images/add-multiple"

        form.add_field("uploaderid", str(interaction.user.id))
        form.add_field("guildid", str(interaction.guild.id))
        form.add_field("title", title)
        status, resp = await post(endpoint, headers=headers, data=form)

        if status != 201:
            await interaction.followup.send(
                f"Failed to upload: {status}", ephemeral=True
            )
            return

        count = len(attachments)
        msg = (
            "Your image has been added to the gallery!"
            if count == 1
            else f"Your {count} images have been added to the gallery!"
        )
        await interaction.followup.send(msg, ephemeral=True)

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

        if status != 204:
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
