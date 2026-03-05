from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv("TOKEN")
BACKEND_URL = os.getenv("BACKEND_URL")
PUBLIC_URL = os.getenv("PUBLIC_URL")
API_SERVICE_TOKEN = os.getenv("API_SERVICE_TOKEN")
if not API_SERVICE_TOKEN:
    raise RuntimeError("Missing required env var: API_SERVICE_TOKEN")
