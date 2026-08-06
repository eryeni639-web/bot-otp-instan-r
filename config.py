import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OTP_API_KEY = os.getenv("OTPINSTAN_API_KEY")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")
