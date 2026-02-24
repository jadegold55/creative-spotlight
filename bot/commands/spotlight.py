import discord
from discord.ext import commands, tasks
import requests

from bot.config import BACKEND_URL, SPOTLIGHT_CHANNEL_ID


class Spotlight(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channel_id = SPOTLIGHT_CHANNEL_ID
        self.spotlight_winner.start()

    def cog_unload(self):
        self.spotlight_winner.cancel()

    @tasks.loop(minutes=5)
    async def spotlight_winner(self):
        if not self.channel_id:
            return

        channel = self.bot.get_channel(self.channel_id)
        if not channel:
            return

        try:
            winner_response = requests.get(
                f"{BACKEND_URL}/images/contests/active/winner", timeout=10
            )
        except requests.RequestException:
            return

        if winner_response.status_code != 200:
            return

        winner = winner_response.json()
        if not winner or winner.get("spotlighted"):
            return

        uploader_id = winner.get("uploaderID") or winner.get("uploaderId")
        image_url = winner.get("url") or winner.get("imageUrl")
        contest_id = winner.get("contestId")

        if not uploader_id or not image_url or not contest_id:
            return

        embed = discord.Embed(
            title="🏆 Spotlight Winner",
            description=(
                f"Congrats <@{uploader_id}>! Your image won the latest contest."
            ),
            color=discord.Color.gold(),
        )
        embed.set_image(url=image_url)

        await channel.send(content=f"<@{uploader_id}>", embed=embed)

        try:
            requests.post(
                f"{BACKEND_URL}/images/contests/{contest_id}/spotlighted",
                params={"imageId": winner.get("id")},
                timeout=10,
            )
        except requests.RequestException:
            return

    @spotlight_winner.before_loop
    async def before_spotlight(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(Spotlight(bot))
