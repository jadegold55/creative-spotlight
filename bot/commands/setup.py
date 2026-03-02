from aiohttp.web_routedef import view
import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View


from bot.apihelper.api import delete, post

TIMEZONE_CHOICES = [
    app_commands.Choice(name="Eastern (ET)", value="America/New_York"),
    app_commands.Choice(name="Central (CT)", value="America/Chicago"),
    app_commands.Choice(name="Mountain (MT)", value="America/Denver"),
    app_commands.Choice(name="Pacific (PT)", value="America/Los_Angeles"),
    app_commands.Choice(name="UTC", value="UTC"),
    app_commands.Choice(name="GMT", value="Europe/London"),
    app_commands.Choice(name="CET", value="Europe/Paris"),
    app_commands.Choice(name="JST", value="Asia/Tokyo"),
]

DAY_CHOICES = [
    app_commands.Choice(name="Monday", value=0),
    app_commands.Choice(name="Tuesday", value=1),
    app_commands.Choice(name="Wednesday", value=2),
    app_commands.Choice(name="Thursday", value=3),
    app_commands.Choice(name="Friday", value=4),
    app_commands.Choice(name="Saturday", value=5),
    app_commands.Choice(name="Sunday", value=6),
]

FEATURE_CHOICES = [
    app_commands.Choice(name="Poems", value="poems"),
    app_commands.Choice(name="Contest", value="contest"),
]


class Setup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    setup_group = app_commands.Group(
        name="setup", description="Setup commands, channels, and events for the bot"
    )

    @setup_group.command(name="poems", description="Configure daily poems")
    @app_commands.describe(poem_channel="Channel for daily poems")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_poems(self, interaction, poem_channel: discord.TextChannel):
        view = TimeSetupView(interaction.guild_id, poem_channel.id, "poems")
        embed = discord.Embed(
            title="📝 Poem Setup",
            description=f"Channel: {poem_channel.mention}\n\nSelect the time for daily poems:",
            color=discord.Color.blue(),
        )
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @setup_group.command(name="contest", description="Configure spotlight contests")
    @app_commands.describe(
        channel="Channel for contests",
        day="Day for weekly contests",
        duration="Duration in days (1-14)",
    )
    @app_commands.choices(day=DAY_CHOICES)
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_spotlight(
        self,
        interaction,
        channel: discord.TextChannel,
        day: app_commands.Choice[int],
        duration: app_commands.Range[int, 1, 14],
    ):
        view = TimeSetupView(
            interaction.guild_id,
            channel.id,
            "contest",
            day=day.value,
            duration=duration,
        )
        embed = discord.Embed(
            title="🏆 Contest Setup",
            description=f"Channel: {channel.mention}\nDay: {day.name}\nDuration: {duration} days\n\nSelect the time:",
            color=discord.Color.gold(),
        )
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @setup_group.command(name="reset", description="reset a current configuration")
    @app_commands.describe(feature="Which configuration to remove")
    @app_commands.choices(feature=FEATURE_CHOICES)
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_remove(
        self,
        interaction: discord.Interaction,
        feature: app_commands.Choice[str],
    ):
        if feature.value == "poems":
            endpoint = "setup-poems"
        elif feature.value == "contest":
            endpoint = "setup-contest"
        status, text = await delete(
            f"guilds/{interaction.guild_id}/{endpoint}",
            headers={
                "X-User-Id": str(interaction.user.id),
                "X-Command": "SubCommandSetupRemove",
            },
        )

        if status != 200:
            await interaction.response.send_message(
                "Failed to save settings. Please try again.", ephemeral=True
            )
            return

        await interaction.response.send_message(
            f"{feature.name} configuration removed successfully!",
            ephemeral=True,
        )


class TimeSetupView(View):
    def __init__(self, guild_id, channel_id, feature, day=None, duration=None):
        super().__init__(timeout=120)
        self.guild_id = guild_id
        self.channel_id = channel_id
        self.feature = feature
        self.day = day
        self.duration = duration
        self.hour = None
        self.minute = None
        self.period = None
        self.timezone = None

    @discord.ui.select(
        placeholder="Hour",
        options=[
            discord.SelectOption(label=str(i), value=str(i)) for i in range(1, 13)
        ],
        min_values=1,
        max_values=1,
        row=0,
    )
    async def hour_select(self, interaction, select):
        self.hour = int(select.values[0])
        await interaction.response.defer()

    @discord.ui.select(
        placeholder="Minute",
        options=[
            discord.SelectOption(label=f":{m:02d}", value=str(m))
            for m in [0, 15, 30, 45]
        ],
        min_values=1,
        max_values=1,
        row=1,
    )
    async def minute_select(self, interaction, select):
        self.minute = int(select.values[0])
        await interaction.response.defer()

    @discord.ui.select(
        placeholder="AM / PM",
        options=[
            discord.SelectOption(label="AM", value="AM"),
            discord.SelectOption(label="PM", value="PM"),
        ],
        min_values=1,
        max_values=1,
        row=2,
    )
    async def period_select(self, interaction, select):
        self.period = select.values[0]
        await interaction.response.defer()

    @discord.ui.select(
        placeholder="Timezone",
        options=[
            discord.SelectOption(label="Eastern (ET)", value="America/New_York"),
            discord.SelectOption(label="Central (CT)", value="America/Chicago"),
            discord.SelectOption(label="Mountain (MT)", value="America/Denver"),
            discord.SelectOption(label="Pacific (PT)", value="America/Los_Angeles"),
            discord.SelectOption(label="UTC", value="UTC"),
            discord.SelectOption(label="GMT", value="Europe/London"),
            discord.SelectOption(label="CET", value="Europe/Paris"),
            discord.SelectOption(label="JST", value="Asia/Tokyo"),
        ],
        min_values=1,
        max_values=1,
        row=3,
    )
    async def timezone_select(self, interaction, select):
        self.timezone = select.values[0]
        await interaction.response.defer()

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.success, row=4)
    async def confirm(self, interaction, button):
        if any(v is None for v in [self.hour, self.minute, self.period, self.timezone]):
            await interaction.response.send_message(
                "Please fill in all fields before confirming.", ephemeral=True
            )
            return

        # Convert to 24hr
        if self.period == "AM":
            hour_24 = 0 if self.hour == 12 else self.hour
        else:
            hour_24 = 12 if self.hour == 12 else self.hour + 12

        if self.feature == "poems":
            status, text = await post(
                f"guilds/{self.guild_id}/setup-poems",
                params={
                    "poemChannelId": self.channel_id,
                    "hour": hour_24,
                    "minute": self.minute,
                    "timezone": self.timezone,
                },
                headers={
                    "X-User-Id": str(interaction.user.id),
                    "X-User-Name": interaction.user.name,
                },
            )
        else:
            status, text = await post(
                f"guilds/{self.guild_id}/setup-contest",
                params={
                    "spotlightChannelId": self.channel_id,
                    "day": self.day,
                    "hour": hour_24,
                    "minute": self.minute,
                    "timezone": self.timezone,
                    "durationDays": self.duration,
                },
                headers={
                    "X-User-Id": str(interaction.user.id),
                    "X-User-Name": interaction.user.name,
                },
            )

        if status != 200:
            await interaction.response.send_message(
                "Failed to save settings. Please try again.", ephemeral=True
            )
            return

        tz_names = {
            "America/New_York": "ET",
            "America/Chicago": "CT",
            "America/Denver": "MT",
            "America/Los_Angeles": "PT",
            "UTC": "UTC",
            "Europe/London": "GMT",
            "Europe/Paris": "CET",
            "Asia/Tokyo": "JST",
        }
        time_str = f"{self.hour}:{self.minute:02d} {self.period} ({tz_names.get(self.timezone, self.timezone)})"

        await interaction.response.edit_message(
            content=f"**{self.feature.title()}** configured!\nChannel: <#{self.channel_id}>\nTime: {time_str}",
            embed=None,
            view=None,
        )
        self.stop()


async def setup(bot):
    await bot.add_cog(Setup(bot))
