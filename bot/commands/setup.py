import discord
from discord import app_commands
from discord.ext import commands
import requests
from bot.config import BACKEND_URL


class Setup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="setup", description="Configure bot channels for this server"
    )
    @app_commands.describe(
        poem_channel="Channel for daily poems",
        spotlight_channel="Channel for weekly art contests",
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def setup(
        self,
        interaction: discord.Interaction,
        poem_channel: discord.TextChannel = None,
        spotlight_channel: discord.TextChannel = None,
    ):
        if not poem_channel and not spotlight_channel:
            await interaction.response.send_message(
                "Please specify at least one channel to configure.", ephemeral=True
            )
            return

        params = {}
        if poem_channel:
            params["poemChannelId"] = poem_channel.id
        if spotlight_channel:
            params["spotlightChannelId"] = spotlight_channel.id

        resp = requests.post(
            f"{BACKEND_URL}/guilds/{interaction.guild_id}/setup",
            params=params,
        )

        if resp.status_code != 200:
            await interaction.response.send_message(
                "Failed to save settings. Please try again.", ephemeral=True
            )
            return

        msg = "Settings updated!\n"
        if poem_channel:
            msg += f"Daily poems → {poem_channel.mention}\n"
        if spotlight_channel:
            msg += f"Weekly contests → {spotlight_channel.mention}"

        await interaction.response.send_message(msg, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Setup(bot))
