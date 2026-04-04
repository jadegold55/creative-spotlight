import asyncio
import logging
from datetime import datetime

import discord
import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord.ext import commands
from discord.ui import Button, View

from bot.apihelper.api import delete, get, post
from bot.config import PUBLIC_URL

log = logging.getLogger(__name__)


def _parse_utc_datetime(value: str | None):
    if not value:
        return None

    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        return pytz.utc.localize(parsed)
    return parsed.astimezone(pytz.utc)


def _format_discord_timestamp(dt: datetime):
    return f"<t:{int(dt.timestamp())}:F>"


class ContestSignupView(View):
    def __init__(self, bot, guild_id: int):
        super().__init__(timeout=None)
        self.bot = bot
        self.guild_id = guild_id

        signup_button = Button(
            label="Sign Up",
            style=discord.ButtonStyle.primary,
            custom_id=f"contest_signup:{guild_id}",
        )
        signup_button.callback = self._on_signup
        self.add_item(signup_button)

    async def _on_signup(self, interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message(
                "Contest signups can only be used inside the server.",
                ephemeral=True,
            )
            return

        member = interaction.guild.get_member(interaction.user.id)
        if member is None:
            try:
                member = await interaction.guild.fetch_member(interaction.user.id)
            except discord.DiscordException:
                member = None

        is_verified = member is not None and not getattr(member, "pending", False)
        headers = {
            "X-User-Id": str(interaction.user.id),
            "X-User-Name": str(interaction.user.name),
        }
        signups = await get(f"contest_signups/{self.guild_id}", headers=headers) or []
        signed_up = any(signup["userId"] == interaction.user.id for signup in signups)

        if signed_up:
            status, _ = await delete(
                f"contest_signups/{self.guild_id}/signup",
                params={"userId": interaction.user.id},
                headers=headers,
            )
            if status == 204:
                await interaction.response.send_message(
                    "You have withdrawn from the contest.",
                    ephemeral=True,
                )
                return

            await interaction.response.send_message(
                "I couldn't remove your signup. Please try again.",
                ephemeral=True,
            )
            return

        status, _ = await post(
            f"contest_signups/{self.guild_id}/signup",
            params={
                "userId": interaction.user.id,
                "username": interaction.user.name,
                "isVerified": str(is_verified).lower(),
            },
            headers=headers,
        )

        if status == 201:
            await interaction.response.send_message(
                "You're signed up. Upload your entry with `/upload` before the deadline.",
                ephemeral=True,
            )
            return

        if status == 403:
            message = "You need to be a verified Discord member before you can sign up."
        elif status == 409:
            message = "Contest signups are closed or you are already signed up."
        else:
            message = "I couldn't complete your signup. Please try again."

        await interaction.response.send_message(message, ephemeral=True)


class Spotlight(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_contests: dict[int, tuple[datetime, dict]] = {}
        self.registered_signup_views: set[int] = set()
        self.scheduler = AsyncIOScheduler(timezone=pytz.utc)
        self._sync_task: asyncio.Task | None = None

    async def cog_load(self):
        self.scheduler.start()
        self._sync_task = asyncio.create_task(self._sync_when_ready())

    def cog_unload(self):
        if self._sync_task is not None:
            self._sync_task.cancel()
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)

    async def _sync_when_ready(self):
        await self.bot.wait_until_ready()
        await self.sync_all_contest_jobs()

    async def _resolve_channel(self, channel_id: int, guild_id: int):
        channel = self.bot.get_channel(channel_id)
        if channel is not None:
            return channel

        try:
            return await self.bot.fetch_channel(channel_id)
        except Exception as e:
            log.warning(
                "Channel lookup failed for guild %s channel %s: %s",
                guild_id,
                channel_id,
                e,
            )
            return None

    def _ensure_signup_view_registered(self, guild_id: int):
        if guild_id in self.registered_signup_views:
            return

        self.bot.add_view(ContestSignupView(self.bot, guild_id))
        self.registered_signup_views.add(guild_id)

    def _job_id(self, guild_id: int, job_type: str):
        return f"contest:{guild_id}:{job_type}"

    def _remove_guild_jobs(self, guild_id: int):
        for job_type in ("start", "end"):
            job = self.scheduler.get_job(self._job_id(guild_id, job_type))
            if job is not None:
                job.remove()

    async def sync_all_contest_jobs(self):
        guilds = await get(
            "guilds/with-spotlight",
            headers={"Bot-User-Id": str(self.bot.user.id)},
        )
        self.active_contests.clear()

        scheduled_guild_ids: set[int] = set()
        if guilds:
            for guild in guilds:
                await self.sync_contest_for_guild(guild["guildId"], guild)
                scheduled_guild_ids.add(guild["guildId"])

        for job in self.scheduler.get_jobs():
            parts = job.id.split(":")
            if len(parts) == 3 and parts[0] == "contest":
                guild_id = int(parts[1])
                if guild_id not in scheduled_guild_ids:
                    job.remove()

    async def sync_contest_for_guild(self, guild_id: int, guild: dict | None = None):
        if guild is None:
            guild = await get(
                f"guilds/{guild_id}",
                headers={"Bot-User-Id": str(self.bot.user.id)},
            )

        self._remove_guild_jobs(guild_id)
        self.active_contests.pop(guild_id, None)

        if not guild or guild.get("spotlightChannelId") is None:
            return

        start_utc = _parse_utc_datetime(guild.get("contestStartAt"))
        end_utc = _parse_utc_datetime(guild.get("contestDeadlineAt"))
        if start_utc is None or end_utc is None:
            return

        self._ensure_signup_view_registered(guild_id)
        now_utc = datetime.now(pytz.utc)

        if now_utc < start_utc:
            self.scheduler.add_job(
                self._run_start_job,
                "date",
                run_date=start_utc,
                id=self._job_id(guild_id, "start"),
                replace_existing=True,
                kwargs={"guild": guild},
            )
            log.info("Scheduled contest start for guild %s at %s UTC", guild_id, start_utc.isoformat())
        elif now_utc < end_utc:
            self.active_contests[guild_id] = (end_utc, guild)
            log.info("Contest already active for guild %s; scheduling end only at %s UTC", guild_id, end_utc.isoformat())

        if now_utc < end_utc:
            self.scheduler.add_job(
                self._run_end_job,
                "date",
                run_date=end_utc,
                id=self._job_id(guild_id, "end"),
                replace_existing=True,
                kwargs={"guild": guild},
            )
            log.info("Scheduled contest end for guild %s at %s UTC", guild_id, end_utc.isoformat())

    async def clear_contest_for_guild(self, guild_id: int):
        self._remove_guild_jobs(guild_id)
        self.active_contests.pop(guild_id, None)

    async def _run_start_job(self, guild: dict):
        await self._start_contest(guild)

    async def _run_end_job(self, guild: dict):
        await self.announce_winner(guild)
        self.active_contests.pop(guild["guildId"], None)
        self._remove_guild_jobs(guild["guildId"])

    async def _start_contest(self, guild):
        gid = guild["guildId"]
        channel_id = guild["spotlightChannelId"]
        deadline_utc = _parse_utc_datetime(guild.get("contestDeadlineAt"))
        log.info("Starting contest announcement for guild %s channel %s", gid, channel_id)

        channel = await self._resolve_channel(channel_id, gid)
        if not channel:
            log.warning(
                "Contest start skipped: no channel found for guild %s channel %s",
                gid,
                channel_id,
            )
            return

        if deadline_utc is None:
            log.warning("Contest start skipped: no deadline found for guild %s", gid)
            return

        try:
            self._ensure_signup_view_registered(gid)
            embed = discord.Embed(
                title="Artist Showcase",
                description=(
                    "Welcome to the contest.\n\n"
                    "Press **Sign Up** below to enter.\n"
                    "You must be a verified Discord member in this server.\n"
                    "Once signed up, submit your work with `/upload` before the deadline."
                ),
                color=discord.Color.gold(),
            )
            embed.add_field(
                name="Deadline",
                value=_format_discord_timestamp(deadline_utc),
                inline=False,
            )
            embed.set_footer(
                text="This contest is a one-time event. Signed-up entries uploaded before the deadline are eligible."
            )

            await channel.send(embed=embed, view=ContestSignupView(self.bot, gid))
            self.active_contests[gid] = (deadline_utc, guild)
            log.info("Contest start message sent for guild %s", gid)
        except Exception as e:
            log.error("Failed to announce contest in guild %s: %s", gid, e)

    async def announce_winner(self, guild):
        gid = guild["guildId"]
        channel_id = guild["spotlightChannelId"]
        channel = await self._resolve_channel(channel_id, gid)
        if not channel:
            log.warning(
                "Winner announcement skipped: no channel found for guild %s channel %s",
                gid,
                channel_id,
            )
            return

        winner = await get(
            "images/contest/winner",
            params={"guildId": guild["guildId"]},
            headers={"Bot-User-Id": str(self.bot.user.id)},
        )
        if not winner:
            await channel.send(
                "The contest has ended, but there were no eligible signed-up submissions with votes."
            )
            return

        embed = discord.Embed(
            title="Contest Winner!",
            description=(
                "Congratulations to "
                f"<@{winner['uploaderId']}> for winning the contest!"
            ),
            color=discord.Color.gold(),
        )
        embed.set_image(url=f"{PUBLIC_URL}/images/{winner['id']}/file")
        embed.set_footer(text=f"Votes: {winner['votes']}")

        try:
            await channel.send(embed=embed)
        except Exception as e:
            log.error("Failed to send winner in guild %s: %s", guild["guildId"], e)


async def setup(bot):
    await bot.add_cog(Spotlight(bot))
