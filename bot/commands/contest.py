import asyncio
import logging
from datetime import datetime, timedelta

import discord
import pytz
from discord.ext import commands

from bot.apihelper.api import get
from bot.config import PUBLIC_URL

log = logging.getLogger(__name__)


def _next_weekly(day, hour, minute, tz):
    """Return the next UTC datetime for a given weekday/time."""
    now = datetime.now(tz)
    target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    days_ahead = (day - now.weekday()) % 7
    target += timedelta(days=days_ahead)
    if target <= now:
        target += timedelta(weeks=1)
    return target.astimezone(pytz.utc)


class Spotlight(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # guild_id -> (end_utc, guild_data)
        self.active_contests: dict = {}
        self._task: asyncio.Task | None = None

    async def cog_load(self):
        self._task = asyncio.create_task(self._contest_loop())

    def cog_unload(self):
        if self._task:
            self._task.cancel()

    async def _contest_loop(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            try:
                guilds = await get(
                    "guilds/with-spotlight",
                    headers={"Bot-User-Id": str(self.bot.user.id)},
                )

                # (utc_time, "start"|"end", guild_data)
                events: list[tuple] = []
                if guilds:
                    for guild in guilds:
                        gid = guild["guildId"]
                        day = guild.get("contestDay")
                        hour = guild.get("contestHour")
                        minute = guild.get("contestMinute")
                        tz_name = guild.get("contestTimezone")
                        duration = guild.get("contestDurationDays")

                        if any(
                            v is None
                            for v in [
                                day,
                                hour,
                                minute,
                                tz_name,
                                duration,
                            ]
                        ):
                            continue

                        try:
                            tz = pytz.timezone(tz_name)
                        except pytz.exceptions.UnknownTimeZoneError:
                            continue

                        # Active contest → schedule end
                        if gid in self.active_contests:
                            end_utc, g = self.active_contests[gid]
                            events.append((end_utc, "end", g))
                        else:
                            target = _next_weekly(day, hour, minute, tz)
                            events.append((target, "start", guild))

                if not events:
                    await asyncio.sleep(60)
                    continue

                events.sort(key=lambda x: x[0])
                next_time = events[0][0]

                await discord.utils.sleep_until(next_time)

                now_utc = datetime.now(pytz.utc)
                for ev_time, ev_type, guild in events:
                    if ev_time > now_utc:
                        break
                    gid = guild["guildId"]
                    if ev_type == "end":
                        await self.announce_winner(guild)
                        self.active_contests.pop(gid, None)
                    elif ev_type == "start":
                        await self._start_contest(guild, now_utc)

            except asyncio.CancelledError:
                raise
            except Exception as e:
                log.error(f"Contest loop error: {e}")
                await asyncio.sleep(60)

    async def _start_contest(self, guild, now_utc):
        gid = guild["guildId"]
        duration = guild["contestDurationDays"]
        channel = self.bot.get_channel(guild["spotlightChannelId"])
        if not channel:
            return
        try:
            await channel.send(
                "@everyone the contest is starting! "
                "Submit your art with the /upload command. "
                "The winner will be announced in "
                f"{duration} days!"
            )
            end_time = now_utc + timedelta(days=duration)
            self.active_contests[gid] = (end_time, guild)
        except Exception as e:
            log.error(f"Failed to announce contest " f"in guild {gid}: {e}")

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
                "The contest has ended, but there were " "no submissions or votes."
            )
            return

        embed = discord.Embed(
            title="Contest Winner!",
            description=(
                "Congratulations to "
                f"<@{winner['uploaderid']}> for "
                "winning this week's contest!"
            ),
            color=discord.Color.gold(),
        )
        embed.set_image(url=f"{PUBLIC_URL}/images/{winner['id']}/file")
        embed.set_footer(text=f"Votes: {winner['votes']}")

        try:
            await channel.send(embed=embed)
        except Exception as e:
            log.error(f"Failed to send winner in " f"guild {guild['guildId']}: {e}")


async def setup(bot):
    await bot.add_cog(Spotlight(bot))
