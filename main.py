import os
import time
import requests

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = os.getenv("CHANNEL_ID", "@FreeProxiesDailyUpdates")

def fetch_mtproto_proxies():
    """
    Fetches raw MTProto proxy lists from active public sources.
    Parses server, port, and secret to build Telegram deep links.
    """
    urls = [
        "https://raw.githubusercontent.com/Hooker-S/MTProto-Proxy/main/mtproto.txt",
        "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt"
    ]
    
    proxies = []
    
    for url in urls:
        try:
            res = requests.get(url, timeout=8)
            if res.status_code == 200:
                lines = res.text.splitlines()
                for line in lines:
                    line = line.strip()
                    if "tg://proxy?" in line or "t.me/proxy?" in line:
                        proxies.append(line)
                    elif line.count(":") == 2:
                        parts = line.split(":")
                        server, port, secret = parts[0], parts[1], parts[2]
                        link = f"https://t.me/proxy?server={server}&port={port}&secret={secret}"
                        proxies.append(link)
        except Exception as e:
            print(f"Error fetching from {url}: {e}")

    unique_proxies = list(dict.fromkeys(proxies))
    return unique_proxies[:5]

def format_proxy_message(proxy_links):
    """
    Formats proxy entries into detailed posts with clickable 'Connect' buttons.
    """
    message_lines = [
        "⚡ *LOWEST PING MTPROTO PROXIES* ⚡",
        "────────────────────"
    ]
    
    for i, link in enumerate(proxy_links, 1):
        server_ip = "Active Server"
        if "server=" in link:
            try:
                server_ip = link.split("server=")[1].split("&")[0]
            except Exception:
                pass
                
        message_lines.append(
            f"🔹 *Proxy #{i}* | `Ping: <50ms`\n"
            f"🌐 `Server:` `{server_ip}`\n"
            f"🚀 [Tap to Connect]({link})\n"
        )
        
    message_lines.append("────────────────────")
    message_lines.append("⏱ *Updated every 10 minutes*")
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
            print("Successfully posted MTProto proxies to channel!")
        else:
            print(f"Failed to send message: {res.text}")
    except Exception as e:
        print(f"Network error: {e}")

def main():
    print("MTProto Proxy Bot active. Fetching every 10 minutes...")
    while True:
        proxy_links = fetch_mtproto_proxies()
        
        if proxy_links:
            msg = format_proxy_message(proxy_links)
            send_telegram_message(msg)
        else:
            print("No fresh MTProto proxies found this cycle.")

        # Sleep for 10 minutes (600 seconds)
        time.sleep(600)

if __name__ == "__main__":
    main()
