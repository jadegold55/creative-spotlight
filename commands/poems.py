import logging
import discord
from discord import app_commands
from discord.ui import Button, View
import os
from discord.ext import commands


from dotenv import load_dotenv
class poetry(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    #scraper will send an ephemeral message of a random poem to someone!
    @app_commands.command(name="poem", description="Get a random poem")
    async def poem(self, interaction: discord.Interaction):
        from scraping.randompoem import scrape
        poem_data = scrape()
        poem_embed = discord.Embed(
            title=poem_data['title'], description=f"By {poem_data['author']}\n\n{poem_data['content']}", color=discord.Color.blue())
        if poem_data:
            
            await interaction.response.send_message("Here's a random poem for you!", embed=poem_embed)
        else:
            await interaction.response.send_message("Sorry, I couldn't fetch a poem at the moment.", ephemeral=True)

#will add  a daily poem event later, but for now this is just a test to make sure the command works and the bot can fetch and display a poem correctly. I will need to add some error handling and logging to make sure it runs smoothly, especially if i want to run it on a schedule.
#commands to add: [poem of the day, poem search, upload poem]
#
async def setup(bot):
    await bot.add_cog(poetry(bot))  