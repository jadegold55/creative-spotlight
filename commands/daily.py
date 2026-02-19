import discord
from discord.ext import commands, tasks
from scraping.randompoem import scrape
import os


class Daily(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channel_id = int(os.getenv("chnl_id"))
        self.daily_poem.start()

    def cog_unload(self):
        self.daily_poem.cancel()

    @tasks.loop(hours=24)
    async def daily_poem(self):
        channel = self.bot.get_channel(self.channel_id)
        if not channel:
            return

        poem_data = scrape()
        if not poem_data:
            return

        embed = discord.Embed(
            title=f"Poem of the Day\n\n{poem_data['title']}",
            description=f"By {poem_data['author']}\n\n{poem_data['content']}",
            color=discord.Color.purple(),
        )
        await channel.send(embed=embed)

    @daily_poem.before_loop
    async def before_daily(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(Daily(bot))
