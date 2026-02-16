import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("TOKEN")
GUILD_ID = os.getenv("GUILD_ID")

#subclass of bot to handle loading extensions and syncing commands on ready
# this structure helps the bot setup be clean and modular, 
#providing a way manage extensions and command syncing. 
# cach extension is developed independently in the "commands" folder, and the bot will automatically load them on startup.
class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=discord.Intents.default(),
            help_command=None
        )

    #setup hook needs to happen so bot can see our commands folder 
    # and load the extensions before the bot is ready. 
    async def setup_hook(self):
        print("--- Loading Extensions ---")
        
        #commands dirrectory finds all python files need in commands
        for filename in os.listdir("./commands"):
            if filename.endswith(".py"):
                try:
                    
                    await self.load_extension(f"commands.{filename[:-3]}")
                    print(f"Loaded succesfully: {filename}")
                except Exception as e:
                    print(f"Failed to load {filename}: {e}")
        
        print("--- Setup Complete ---")

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        
        #this will scale to more guilds if i end up adding them later
        if GUILD_ID:
            try:
                # syncing commands to the specified guild allows for much faster updates 
                # during development, as global command changes can take up to an hour 
                # to propagate.               
                guild_object = discord.Object(id=int(GUILD_ID))
                #self.try.copyglobal makes it so global commands are synced to server
                self.tree.copy_global_to(guild=guild_object)
                #bot looks at command tree in commmands folder and syncs to guild
                #it will specify all commands synced
                
                synced = await self.tree.sync(guild=guild_object)
                print(f"Synced {len(synced)} commands to guild {GUILD_ID}")
                for command in synced:
                    print(f"  - {command.name}" + "\n" + f"    Type: {command.type}" + "\n" + f"    Description: {command.description}")
            except Exception as e:
                print(f"Error syncing: {e}")
        

client = MyBot()
client.run(TOKEN)

