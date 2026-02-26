import discord
from discord.ext import commands, tasks
import requests
from bot.config import BACKEND_URL, SPOTLIGHT_CHANNEL_ID
import asyncio


class Spotlight(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.weekly_contest.start()

    def cog_unload(self):
        self.weekly_contest.cancel()

    @tasks.loop(hours=168)
    async def weekly_contest(self):
        resp = requests.get(f"{BACKEND_URL}/guilds/with-spotlight")
        if resp.status_code != 200:
            return

        guilds = resp.json()

        for guild in guilds:
            channel = self.bot.get_channel(guild["spotlightChannelId"])
            if not channel:
                continue
            try:
                await channel.send(
                    "@everyone the contest is starting! Submit your art with the /upload command. The winner will be announced in 7 days!"
                )
            except Exception as e:
                print(f"Failed to announce contest in guild {guild['guildId']}: {e}")

        await asyncio.sleep(7 * 24 * 60 * 60)

        for guild in guilds:
            channel = self.bot.get_channel(guild["spotlightChannelId"])
            if not channel:
                continue

            response = requests.get(
                f"{BACKEND_URL}/images/contest/winner",
                params={"guildid": guild["guildId"]},
            )
            if response.status_code != 200:
                await channel.send(
                    "The contest has ended, but there was an issue retrieving the winner."
                )
                continue

            winner = response.json()
            embed = discord.Embed(
                title="Contest Winner!",
                description=f"Congratulations to <@{winner['uploaderid']}> for winning this week's contest!",
                color=discord.Color.gold(),
            )
            embed.set_image(url=winner["url"])
            embed.set_footer(text=f"Votes: {winner['votes']}")
            try:
                await channel.send(embed=embed)
            except Exception as e:
                print(f"Failed to send winner in guild {guild['guildId']}: {e}")

    @weekly_contest.before_loop
    async def before_weekly(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(Spotlight(bot))
