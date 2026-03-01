import discord
from discord.ext import commands, tasks
import asyncio
from bot.apihelper.api import get
from datetime import datetime
import pytz

from bot.config import PUBLIC_URL


class Spotlight(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_contests = {}
        self.check_contest.start()

    def cog_unload(self):
        self.check_contest.cancel()

    @tasks.loop(minutes=1)
    async def check_contest(self):
        guilds = await get(
            f"guilds/with-spotlight", headers={"Bot-User-Id": str(self.bot.user.id)}
        )
        if not guilds:
            return
        now_utc = datetime.now(pytz.utc)
        for guild in guilds:
            guild_id = guild["guildId"]
            day = guild.get("contestDay")
            hour = guild.get("contestHour")
            minute = guild.get("contestMinute")
            tz_name = guild.get("contestTimezone")
            duration = guild.get("contestDurationDays")

            if any(v is None for v in [day, hour, minute, tz_name, duration]):
                continue

            try:
                tz = pytz.timezone(tz_name)
            except pytz.exceptions.UnknownTimeZoneError:
                continue

            now = datetime.now(tz)

            # Check if we need to announce a winner for an active contest
            if guild_id in self.active_contests:
                if now_utc >= self.active_contests[guild_id]:
                    await self.announce_winner(guild)
                    del self.active_contests[guild_id]
                continue

            # Check if it's time to start a new contest
            if now.weekday() == day and now.hour == hour and now.minute == minute:
                channel = self.bot.get_channel(guild["spotlightChannelId"])
                if not channel:
                    continue

                try:
                    await channel.send(
                        f"@everyone the contest is starting! Submit your art with the /upload command. "
                        f"The winner will be announced in {duration} days!"
                    )
                    # Store when this contest ends
                    from datetime import timedelta

                    end_time = now_utc + timedelta(days=duration)
                    self.active_contests[guild_id] = end_time
                except Exception as e:
                    print(f"Failed to announce contest in guild {guild_id}: {e}")

    async def announce_winner(self, guild):
        channel = self.bot.get_channel(guild["spotlightChannelId"])
        if not channel:
            return

        winner = await get(
            "/images/contest/winner",
            params={"guildid": guild["guildId"]},
            headers={"Bot-User-Id": str(self.bot.user.id)},
        )
        if not winner:
            await channel.send(
                "The contest has ended, but there were no submissions or votes."
            )
            return

        embed = discord.Embed(
            title="Contest Winner!",
            description=f"Congratulations to <@{winner['uploaderid']}> for winning this week's contest!",
            color=discord.Color.gold(),
        )
        embed.set_image(url=f"{PUBLIC_URL}/images/{winner['id']}/file")
        embed.set_footer(text=f"Votes: {winner['votes']}")

        try:
            await channel.send(embed=embed)
        except Exception as e:
            print(f"Failed to send winner in guild {guild['guildId']}: {e}")

    @check_contest.before_loop
    async def before_check_contest(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(Spotlight(bot))
