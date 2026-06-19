import requests
import os
import time
import html
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

def send_with_retry(url, payload, max_retries=3, as_json=True):
    """Robust networking helper featuring explicit error reporting."""
    for i in range(max_retries):
        try:
            if as_json:
                response = requests.post(url, json=payload, timeout=10)
            else:
                response = requests.post(url, data=payload, timeout=10)
            
            if response.status_code in [200, 204]:
                return True
            else:
                print(f"API Error (Status {response.status_code}): {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"Network glitch (Attempt {i+1}/{max_retries}): {e}")
            time.sleep(2 * (i + 1))
    return False

def send_telegram(message):
    if not TOKEN or not CHAT_ID:
        print("Telegram Credentials Missing!")
        return False
        
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    # Escaping prevent breakages caused by loose characters matching HTML sequences
    safe_message = html.escape(message)
    payload = {"chat_id": CHAT_ID, "text": safe_message, "parse_mode": "HTML"}
    return send_with_retry(url, payload)

def send_telegram_photo(photo_url, caption):
    if not TOKEN or not CHAT_ID:
        print("Telegram Credentials Missing!")
        return False
        
    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
    safe_caption = html.escape(caption)
    payload = {
        "chat_id": CHAT_ID,
        "photo": photo_url,
        "caption": safe_caption,
        "parse_mode": "HTML"
    }
    # Passing photo strings via clean JSON payload matches Telegram standard expectations seamlessly
    return send_with_retry(url, payload, as_json=True)

def send_discord(message):
    if not WEBHOOK_URL:
        print("Discord Webhook Endpoint Missing!")
        return False
        
    payload = {"content": message}
    return send_with_retry(WEBHOOK_URL, payload)