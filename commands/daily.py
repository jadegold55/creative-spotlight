import discord
from discord.ext import commands, tasks
from scraping.randompoem import scrape
from config import CHANNEL_ID


class Daily(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channel_id = CHANNEL_ID
        self.daily_poem.start()

    def cog_unload(self):
        self.daily_poem.cancel()

    @tasks.loop(hours=24)
    async def daily_poem(self):
        print("loop fired")
        channel = self.bot.get_channel(self.channel_id)
        print(f"{channel}")
        if not channel:
            return

        poem_data = scrape()
        if not poem_data:
            print("uh oh")
            return

        embed = discord.Embed(
            title=f"Poem of the Day\n\n{poem_data['title']}",
            description=f"By {poem_data['author']}\n\n{poem_data['content']}",
            color=discord.Color.purple(),
        )
        await channel.send("@everyone", embed=embed)

    @daily_poem.before_loop
    async def before_daily(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(Daily(bot))
