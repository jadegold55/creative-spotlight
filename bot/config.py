from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv("TOKEN")
BACKEND_URL = os.getenv("BACKEND_URL")
PUBLIC_URL = os.getenv("PUBLIC_URL")
