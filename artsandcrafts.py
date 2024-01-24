import discord
from discord.ext import commands
from os import environ as env
from dotenv import load_dotenv

load_dotenv()

token = env["TOKEN"]


class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(
            command_prefix=commands.when_mentioned_or("."), intents=intents
        )

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print("-------")


class Counter(discord.ui.View):
    # number = 5
    # this is the base from which the bots first comman will start
    # what would be good to start with is figuring out how to make a next and previous button, these buttons will show a picture and
    # a description of the picture.
    # for a previous and next button, is making a button object better?
    # or having two functions to define the interaction
    # @discord.ui.button(label='0', style=discord.ButtonStyle.blurple)
    # def counter(self, interaction: discord.Interaction, button: discord.ButtonStyle.blurple):
    global number
    number = 0

    @discord.ui.button(label="prev", style=discord.ButtonStyle.red)
    async def prev(self, interaction: discord.Interaction, button: discord.ui.Button):
        global number
        # number = int(button.label) if button.label else 0
        # if number + 1 >= 5:
        #     button.style = discord.ButtonStyle.green
        #     button.disabled = True
        # button.label = str(number + 1)
        number -= 1
        if number <= 0:
            number = 0
        # await Counter.counter(hey, interaction, button, str(Counter.number))
        await interaction.response.edit_message(view=self, content=number)

    @discord.ui.button(label="next", style=discord.ButtonStyle.grey)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        global number
        number += 1
        if number >= 5:
            number = 5

        # await Counter.counter(, interaction, button, str(Counter.number))
        await interaction.response.edit_message(view=self, content=number)

        # Make sure to update the message with our updated selves


class EphemeralSpotlight(discord.ui.View):
    @discord.ui.button(label="click", style=discord.ButtonStyle.blurple)
    async def receive(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.send_message(
            "Enjoy!", view=Counter(), ephemeral=True
        )


bot = Bot()


@bot.command()
async def hi(ctx):
    await ctx.send("hi", view=EphemeralSpotlight())


bot.run(token=token)
