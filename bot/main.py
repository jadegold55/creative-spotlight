import logging

import discord
from discord.ext import commands
import os
from bot.config import TOKEN
from bot.apihelper.api import close_session
import sys

sys.stdout.reconfigure(line_buffering=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("bot")


# subclass of bot to handle loading extensions and syncing commands on ready
# this structure helps the bot setup be clean and modular,
# providing a way manage extensions and command syncing.
# cach extension is developed independently in the "commands" folder, and the bot will automatically load them on startup.
class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents, help_command=None)

    # setup hook needs to happen so bot can see our commands folder
    # and load the extensions before the bot is ready.
    async def setup_hook(self):
        log.info("--- Loading Extensions ---")
        self.tree.on_error = self.on_app_command_error

        commands_dir = os.path.join(os.path.dirname(__file__), "commands")
        for filename in os.listdir(commands_dir):
            if filename.endswith(".py"):
                try:
                    await self.load_extension(f"bot.commands.{filename[:-3]}")
                    log.info(f"Loaded: {filename}")
                except Exception as e:
                    log.error(f"Failed to load {filename}: {e}")

        log.info("--- Setup Complete ---")

    async def on_ready(self):
        log.info(f"Logged in as {self.user} (ID: {self.user.id})")
        try:
            synced = await self.tree.sync()
            for command in synced:
                log.info(f"  - {command.name}")
        except Exception as e:
            log.error(f"Error syncing: {e}")

    async def on_message(self, message):
        if message.author.bot:
            return
        if "meow" in message.content.lower():
            await message.channel.send("meow")
        await self.process_commands(message)

    async def on_app_command_error(self, interaction, error):
        if isinstance(error, discord.app_commands.CommandOnCooldown):
            embed = discord.Embed(
                title="Slow down!",
                description=f"Try again in **{error.retry_after:.0f}** seconds.",
                color=discord.Color.orange(),
            )
        else:
            embed = discord.Embed(
                title="Something went wrong",
                description="An error occurred while processing the command.",
                color=discord.Color.red(),
            )
            log.error(f"Error in command {interaction.command.name}: {error}")

        if interaction.response.is_done():
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message(embed=embed, ephemeral=True)

    async def close(self):
        await close_session()
        await super().close()


client = MyBot()
client.run(TOKEN)
