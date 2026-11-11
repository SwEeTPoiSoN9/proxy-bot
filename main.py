import os
import time
import random
import requests

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = os.getenv("CHANNEL_ID", "@FreeProxiesDailyUpdates")

def fetch_mtproto_proxies():
    """
    Fetches proxy feeds and randomly selects a fresh batch every cycle.
    """
    urls = [
        "https://raw.githubusercontent.com/0xRadikal/Free-Telegram-Proxy/main/resilient/tme.txt",
        "https://raw.githubusercontent.com/SoliSpirit/mtproto/master/all_proxies.txt",
        "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt"
    ]
    
    proxies = []
    
    for url in urls:
        try:
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                for line in res.text.splitlines():
                    line = line.strip()
                    if "t.me/proxy?" in line or "tg://proxy?" in line:
                        proxies.append(line)
        except Exception as e:
            print(f"Error fetching from {url}: {e}")

    # Remove duplicates
    unique_proxies = list(dict.fromkeys(proxies))
    
    # Pick 5 random unique proxies so it changes every single time
    if len(unique_proxies) >= 5:
        return random.sample(unique_proxies, 5)
    elif unique_proxies:
        random.shuffle(unique_proxies)
        return unique_proxies
    else:
        # Emergency rotating fallback list
        fallback = [
            "https://t.me/proxy?server=149.154.167.99&port=443&secret=ee160301020001000100000000000000",
            "https://t.me/proxy?server=91.108.56.170&port=443&secret=ee888888888888888888888888888888",
            "https://t.me/proxy?server=149.154.160.115&port=443&secret=ee160301020001000100000000000000",
            "https://t.me/proxy?server=149.154.167.220&port=443&secret=ee160301020001000100000000000000"
        ]
        random.shuffle(fallback)
        return fallback[:3]

def format_proxy_message(proxy_links):
    message_lines = [
        "⚡ *FRESH ROTATING MTPROTO PROXIES* ⚡",
        "────────────────────"
    ]
    
    for i, link in enumerate(proxy_links, 1):
        server_ip = "Proxy Node"
        if "server=" in link:
            try:
                server_ip = link.split("server=")[1].split("&")[0]
            except Exception:
                pass
                
        message_lines.append(
            f"🔹 *Proxy #{i}*\n"
            f"🌐 `Server:` `{server_ip}`\n"
            f"🚀 [Tap to Connect]({link})\n"
        )
        
    message_lines.append("────────────────────")
    message_lines.append("⏱ *Updated every 10 minutes (New Batch)*")
    message_lines.append("📢 *Channel:* @FreeProxiesDailyUpdates")
    message_lines.append("💼 *Support (ERC20/BSC):*\n`0x327bd2c712a13cf19c0ae63814bdb27664e9933c`")
    
    return "\n".join(message_lines)

def send_telegram_message(text):
    if not BOT_TOKEN:
        print("Error: BOT_TOKEN is missing!")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_USERNAME,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }

    try:
        res = requests.post(url, json=payload, timeout=10)
        if res.status_code == 200:
            print("Successfully posted new random proxy batch!")
        else:
            print(f"Failed to send message: {res.text}")
    except Exception as e:
        print(f"Network error: {e}")

def main():
    print("MTProto Proxy Bot active with random rotation every 10 minutes...")
    while True:
        proxy_links = fetch_mtproto_proxies()
        
        if proxy_links:
            msg = format_proxy_message(proxy_links)
            send_telegram_message(msg)
        else:
            print("No proxies retrieved this cycle.")

        time.sleep(600)

if __name__ == "__main__":
    main()
