import requests
import os
import time
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

def send_with_retry(url, payload, max_retries=3):
    """Professional helper to send requests with a built-in retry mechanism."""
    for i in range(max_retries):
        try:
            response = requests.post(url, json=payload, timeout=10) # Added 10s timeout
            if response.status_code in [200, 204]:
                return True
        except requests.exceptions.RequestException as e:
            print(f"Connection issue (Attempt {i+1}): {e}")
            time.sleep(2 * (i + 1)) # Wait longer each time
    return False

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    return send_with_retry(url, payload)

def send_discord(message):
    payload = {"content": message}
    return send_with_retry(WEBHOOK_URL, payload)