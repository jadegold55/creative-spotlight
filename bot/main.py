import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
from bot.config import TOKEN
import sys

sys.stdout.reconfigure(line_buffering=True)


# subclass of bot to handle loading extensions and syncing commands on ready
# this structure helps the bot setup be clean and modular,
# providing a way manage extensions and command syncing.
# cach extension is developed independently in the "commands" folder, and the bot will automatically load them on startup.
class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!", intents=discord.Intents.default(), help_command=None
        )

    # setup hook needs to happen so bot can see our commands folder
    # and load the extensions before the bot is ready.
    async def setup_hook(self):
        print("--- Loading Extensions ---")
        self.tree.on_error = self.on_app_command_error

        # commands dirrectory finds all python files need in commands
        commands_dir = os.path.join(os.path.dirname(__file__), "commands")
        for filename in os.listdir(commands_dir):
            if filename.endswith(".py"):
                try:

                    await self.load_extension(f"bot.commands.{filename[:-3]}")
                    print(f"Loaded succesfully: {filename}")
                except Exception as e:
                    print(f"Failed to load {filename}: {e}")

        print("--- Setup Complete ---")

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        try:
            # old_guild = discord.Object(id=)
            # self.tree.clear_commands(guild=old_guild)
            # await self.tree.sync(guild=old_guild)
            # print("Cleared old guild commands")

            # Sync globally
            synced = await self.tree.sync()
            for command in synced:
                print(f"  - {command.name}")
        except Exception as e:
            print(f"Error syncing: {e}")

    async def on_app_command_error(self, interaction, error):
        if isinstance(error, discord.app_commands.CommandOnCooldown):
            embed = discord.Embed(
                title="Slow down!",
                description=f"Try again in **{error.retry_after:.0f}** seconds.",
                color=discord.Color.orange(),
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

        else:
            embed = discord.Embed(
                title="Something went wrong",
                description="An error occurred while processing the command.",
                color=discord.Color.red(),
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            print(f"Error in command {interaction.command.name}: {error}")


client = MyBot()
client.run(TOKEN)
