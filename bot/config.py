from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv("TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))
CHANNEL_ID = int(os.getenv("chnl_id"))
BACKEND_URL = os.getenv("BACKEND_URL")
SPOTLIGHT_CHANNEL_ID = int(os.getenv("SPOTLIGHT_CHANNEL_ID"))
