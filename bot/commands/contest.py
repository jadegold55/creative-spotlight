import discord
from discord.ext import commands, tasks
import requests
from bot.config import BACKEND_URL, SPOTLIGHT_CHANNEL_ID
import asyncio


class Spotlight(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.channel_id = SPOTLIGHT_CHANNEL_ID
        self.announced_contests = set()
        self.weekly_contest.start()

    def cog_unload(self):
        self.weekly_contest.cancel()

    @tasks.loop(hours=168)
    async def weekly_contest(self):

        print("fired")
        channel = self.bot.get_channel(self.channel_id)
        if not channel:
            return
        await channel.send(
            "@everyone the contest is starting! Submit your art with the /upload command. The winner will be announced in 7 days!"
        )
        await asyncio.sleep(7 * 24 * 60 * 60)  # Sleep for 7 days
        response = requests.get(f"{BACKEND_URL}/images/contest/winner")
        if response.status_code != 200:
            await channel.send(
                "The contest has ended, but there was an issue retrieving the winner. Please check back later!"
            )
            return
        winner = response.json()
        if not winner:
            await channel.send(
                "The contest has ended, but there were no submissions. Better luck next time!"
            )
            return
        embed = discord.Embed(
            title="Contest Winner!",
            description=f"Congratulations to <@{winner['uploaderid']}> for winning this week's contest with their submission!",
            color=discord.Color.gold(),
        )
        embed.set_image(url=winner["url"])
        embed.set_footer(text=f"Votes: {winner['votes']}")
        await channel.send(embed=embed)

    @weekly_contest.before_loop
    async def before_weekly(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(Spotlight(bot))
