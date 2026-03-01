import discord
from discord.ext import commands, tasks
from bot.scraping.randompoem import scrape
from bot.apihelper.api import get
from datetime import datetime
import pytz


class Daily(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.daily_poem.start()

    def cog_unload(self):
        self.daily_poem.cancel()

    @tasks.loop(minutes=1)
    async def daily_poem(self):
        guilds = await get(
            f"guilds/with-poems", headers={"Bot-User-Id": str(self.bot.user.id)}
        )
        if not guilds:
            return
        for guild in guilds:
            hour = guild.get("poemHour")
            minute = guild.get("poemMinute")
            tz_name = guild.get("poemTimezone")
            if hour is None or minute is None or not tz_name:
                continue
            try:
                tz = pytz.timezone(tz_name)
            except pytz.exceptions.UnknownTimeZoneError:
                continue
            now = datetime.now(tz)
            if now.hour == hour and now.minute == minute:
                channel = self.bot.get_channel(guild["poemChannelId"])
                if not channel:
                    continue

                poem_data = scrape()
                if not poem_data:
                    continue
                embed = discord.Embed(
                    title=f"Poem of the Day\n\n{poem_data['title']}",
                    description=f"By {poem_data['author']}\n\n{poem_data['content']}",
                    color=discord.Color.purple(),
                )
                try:
                    await channel.send("@everyone", embed=embed)
                except Exception as e:
                    print(f"Failed to send poem to guild {guild['guildId']}: {e}")

    @daily_poem.before_loop
    async def before_daily(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(Daily(bot))
