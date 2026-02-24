import discord
from discord.ext import commands, tasks
import requests

from bot.config import BACKEND_URL, SPOTLIGHT_CHANNEL_ID


class Spotlight(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channel_id = SPOTLIGHT_CHANNEL_ID
        self.announced_contests = set()
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
            images_response = requests.get(f"{BACKEND_URL}/images/all", timeout=10)

        except requests.RequestException:
            return

        if images_response.status_code != 200:
            return

        winner = images_response.json()
        images = images_response.json()
        contest_ids = {
            image.get("contestId")
            for image in images
            if image.get("contestId") is not None and image.get("contestDeadline")
        }

        if not contest_ids:
            return

        for contest_id in sorted(contest_ids, reverse=True):
            if contest_id in self.announced_contests:
                continue

            try:
                winner_response = requests.get(
                    f"{BACKEND_URL}/images/contests/{contest_id}/winner", timeout=10
                )
            except requests.RequestException:
                continue

            if winner_response.status_code != 200:
                # 409 = contest still active. Other non-200 means no winner yet.
                continue

            winner = winner_response.json()
            uploader_id = winner.get("uploaderId") or winner.get("uploaderID")
            image_url = winner.get("imageUrl") or winner.get("url")
            vote_count = winner.get("voteCount")

            if uploader_id is None or not image_url:
                continue

            embed = discord.Embed(
                title="🏆 Spotlight Winner",
                description=(
                    f"Congrats <@{uploader_id}>! Your image won contest #{contest_id}."
                ),
                color=discord.Color.gold(),
            )
            embed.set_image(url=image_url)
            if vote_count is not None:
                embed.set_footer(text=f"Final votes: {vote_count}")

            await channel.send(content=f"<@{uploader_id}>", embed=embed)

            self.announced_contests.add(contest_id)
            return


async def setup(bot):
    await bot.add_cog(Spotlight(bot))
