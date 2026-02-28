import discord
from discord import app_commands

from discord.ext import commands


class poetry(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.command(name="poem", description="Get a random poem")
    @app_commands.describe(author="Enter by Author", title="Enter by title")
    async def poem(
        self, interaction: discord.Interaction, author: str = None, title: str = None
    ):
        from scraping.randompoem import scrape

        poem_data = scrape(author=author, title=title)
        if not poem_data:
            await interaction.response.send_message(
                "Sorry, I couldn't fetch a poem at the moment.", ephemeral=True
            )
            return
        # find a workaround for users that ask for a title that has content length > 4096

        poem_embed = discord.Embed(
            title=poem_data["title"],
            description=f"By {poem_data['author']}\n\n{poem_data['content']}",
            color=discord.Color.blue(),
        )
        # if not empty, don't want to be empty or might be logic in randompoem

        await interaction.response.send_message(
            f"Here's a poem by {poem_data['author']}", embed=poem_embed
        )


# will add  a daily poem event later, but for now this is just a test to make sure the command works and the bot can fetch and display a poem correctly. I will need to add some error handling and logging to make sure it runs smoothly, especially if i want to run it on a schedule.
# commands to add: [poem of the day, poem search, upload poem]


async def setup(bot):
    await bot.add_cog(poetry(bot))
