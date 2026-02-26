import discord
from discord.ext import commands, tasks
from bot.scraping.randompoem import scrape
from bot.config import BACKEND_URL
import requests


class Daily(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.daily_poem.start()

    def cog_unload(self):
        self.daily_poem.cancel()

    @tasks.loop(hours=24)
    async def daily_poem(self):
        resp = requests.get(f"{BACKEND_URL}/guilds/with-poems")
        if resp.status_code != 200:
            return

        guilds = resp.json()
        poem_data = scrape()
        if not poem_data:
            return

        embed = discord.Embed(
            title=f"Poem of the Day\n\n{poem_data['title']}",
            description=f"By {poem_data['author']}\n\n{poem_data['content']}",
            color=discord.Color.purple(),
        )

        for guild in guilds:
            channel = self.bot.get_channel(guild["poemChannelId"])
            if channel:
                try:
                    await channel.send("@everyone", embed=embed)
                except Exception as e:
                    print(f"Failed to send poem to guild {guild['guildId']}: {e}")

    @daily_poem.before_loop
    async def before_daily(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(Daily(bot))
