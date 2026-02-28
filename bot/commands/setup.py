import discord
from discord import app_commands
from discord.ext import commands


from bot.apihelper.api import post

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


class Setup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    setup_group = app_commands.Group(
        name="setup", description="Setup commands, channels, and events for the bot"
    )

    @setup_group.command(
        name="poems", description="Configure bot channels for this server"
    )
    @app_commands.describe(
        poem_channel="Channel for daily poems",
        hour="Hour for daily poems",
        minute="Minute for daily poems",
        timezone="Timezone for daily poems",
    )
    @app_commands.choices(timezone=TIMEZONE_CHOICES)
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_poems(
        self,
        interaction: discord.Interaction,
        poem_channel: discord.TextChannel,
        hour: app_commands.Range[int, 0, 23],
        minute: app_commands.Range[int, 0, 59],
        timezone: app_commands.Choice[str],
    ):
        if not poem_channel:
            await interaction.response.send_message(
                "Please specify at least one channel to configure.", ephemeral=True
            )
            return

        status, text = await post(
            f"guilds/{interaction.guild_id}/setup-poems",
            params={
                "poemChannelId": poem_channel.id,
                "hour": hour,
                "minute": minute,
                "timezone": timezone.value,
            },
        )
        if status != 200:
            await interaction.response.send_message(
                "Failed to save settings. Please try again.", ephemeral=True
            )
            return

        time_str = f"{hour:02d}:{minute:02d}"
        await interaction.response.send_message(
            f"Daily poems configured!\n"
            f"Channel: {poem_channel.mention}\n"
            f"Time: {time_str} ({timezone.name})",
            ephemeral=True,
        )

    @setup_group.command(
        name="contest", description="Configure bot channels for this server"
    )
    @app_commands.describe(
        channel="Channel for weekly spotlight contests",
        day="Day for weekly spotlight contests",
        hour="Hour for weekly spotlight contests",
        minute="Minute for weekly spotlight contests",
        timezone="Timezone for weekly spotlight contests",
        duration="Duration of the contest in days (1-14)",
    )
    @app_commands.choices(day=DAY_CHOICES, timezone=TIMEZONE_CHOICES)
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_spotlight(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        day: app_commands.Choice[int],
        hour: app_commands.Range[int, 0, 23],
        minute: app_commands.Range[int, 0, 59],
        timezone: app_commands.Choice[str],
        duration: app_commands.Range[int, 1, 14],
    ):
        status, text = await post(
            f"guilds/{interaction.guild_id}/setup-contest",
            params={
                "spotlightChannelId": channel.id,
                "day": day.value,
                "hour": hour,
                "minute": minute,
                "timezone": timezone.value,
                "durationDays": duration,
            },
        )

        if status != 200:
            await interaction.response.send_message(
                "Failed to save settings. Please try again.", ephemeral=True
            )
            return

        time_str = f"{hour:02d}:{minute:02d}"
        await interaction.response.send_message(
            f"Weekly spotlight contests configured!\n"
            f"Channel: {channel.mention}\n"
            f"Time: {time_str} ({timezone.name}) on {day.name}\n"
            f"Duration: {duration} days",
            ephemeral=True,
        )


async def setup(bot):
    await bot.add_cog(Setup(bot))
