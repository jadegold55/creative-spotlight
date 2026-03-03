import asyncio
import logging
from datetime import datetime, timedelta

import discord
import pytz
from discord.ext import commands

from bot.apihelper.api import get
from bot.scraping.randompoem import scrape

log = logging.getLogger(__name__)


def _next_daily(hour, minute, tz):
    """Return the next UTC datetime for a given local hour:minute."""
    now = datetime.now(tz)
    target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if target <= now:
        target += timedelta(days=1)
    return target.astimezone(pytz.utc)


class Daily(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._task: asyncio.Task | None = None

    async def cog_load(self):
        self._task = asyncio.create_task(self._poem_loop())

    def cog_unload(self):
        if self._task:
            self._task.cancel()

    async def _poem_loop(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            try:
                guilds = await get(
                    "guilds/with-poems",
                    headers={"Bot-User-Id": str(self.bot.user.id)},
                )

                schedule = []  # (utc_target, guild_data)
                if guilds:
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
                        target = _next_daily(hour, minute, tz)
                        schedule.append((target, guild))

                if not schedule:
                    await asyncio.sleep(60)
                    continue

                schedule.sort(key=lambda x: x[0])
                next_time = schedule[0][0]

                # sleep until the earliest event
                await discord.utils.sleep_until(next_time)

                # fire for every guild whose target <= now
                now_utc = datetime.now(pytz.utc)
                for target, guild in schedule:
                    if target > now_utc:
                        break
                    await self._send_poem(guild)

            except asyncio.CancelledError:
                raise
            except Exception as e:
                log.error(f"Poem loop error: {e}")
                await asyncio.sleep(60)

    async def _send_poem(self, guild):
        channel = self.bot.get_channel(guild["poemChannelId"])
        if not channel:
            return
        poem_data = await asyncio.to_thread(scrape)
        if not poem_data:
            return
        embed = discord.Embed(
            title=f"Poem of the Day\n\n{poem_data['title']}",
            description=(f"By {poem_data['author']}\n\n" f"{poem_data['content']}"),
            color=discord.Color.purple(),
        )
        try:
            await channel.send("@everyone", embed=embed)
        except Exception as e:
            log.error(f"Failed to send poem to " f"guild {guild['guildId']}: {e}")


async def setup(bot):
    await bot.add_cog(Daily(bot))
