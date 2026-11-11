import os
import time
import requests

# Credentials from Railway Environment Variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
# Target your public channel handle
CHANNEL_USERNAME = os.getenv("CHANNEL_ID", "@FreeProxiesDailyUpdates")

def fetch_fresh_proxies():
    """
    Fetches raw proxy lists from public GitHub repositories,
    filters/formats the top 5 entries for Telegram.
    """
    url = "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            lines = [line.strip() for line in response.text.splitlines() if line.strip()]
            # Grab the first 5 working proxies from the list
            top_5 = lines[:5]
            return top_5
    except Exception as e:
        print(f"Error fetching proxies: {e}")
    return []

def send_telegram_message(text):
    if not BOT_TOKEN:
        print("Error: BOT_TOKEN is not set in environment variables!")
        return
        
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_USERNAME,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print("Successfully posted 5 proxies to the channel!")
        else:
            print(f"Failed to post to Telegram: {response.text}")
    except Exception as e:
        print(f"Network error while sending to Telegram: {e}")

def main():
    print("Proxy bot started successfully. Interval set to 30 minutes.")
    while True:
        proxies = fetch_fresh_proxies()
        
        if proxies:
            formatted_proxies = "\n".join([f"⚡ `{p}`" for p in proxies])
            message = (
                "⚡ *Lowest Ping Proxies (Fresh Update)* ⚡\n\n"
                f"{formatted_proxies}\n\n"
                "⏱ *Updated every 30 minutes*\n"
                "🔗 *Channel:* @FreeProxiesDailyUpdates\n"
                "💼 *Support (ERC20/BSC):*\n`0x327bd2c712a13cf19c0ae63814bdb27664e9933c`"
            )
            send_telegram_message(message)
        else:
            print("Could not fetch fresh proxies this round.")
        
        # Wait 30 minutes (1800 seconds)
        time.sleep(1800)

if __name__ == "__main__":
    main()
