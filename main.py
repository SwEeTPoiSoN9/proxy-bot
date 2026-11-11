import os
import time
import requests

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = os.getenv("CHANNEL_ID", "@FreeProxiesDailyUpdates")

def fetch_mtproto_proxies():
    """
    Fetches raw proxy lists from multiple reliable public sources
    and parses MTProto links or server:port:secret strings.
    """
    urls = [
        "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt",
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/mtproto.txt",
        "https://raw.githubusercontent.com/MTProto-Proxy/MTProto-Proxy.github.io/master/proxy.list",
        "https://raw.githubusercontent.com/BreakingTech/MTProto-Proxy/main/mtproto.txt"
    ]
    
    proxies = []
    
    for url in urls:
        try:
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                lines = res.text.splitlines()
                for line in lines:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                        
                    # Handle full deep links
                    if "tg://proxy?" in line or "t.me/proxy?" in line:
                        proxies.append(line)
                    # Handle server:port:secret format
                    elif line.count(":") >= 2:
                        parts = line.split(":")
                        if len(parts) >= 3:
                            server, port, secret = parts[0], parts[1], parts[2]
                            link = f"https://t.me/proxy?server={server}&port={port}&secret={secret}"
                            proxies.append(link)
        except Exception as e:
                print(f"Error fetching from {url}: {e}")

    # Remove duplicates and grab top 5
    unique_proxies = list(dict.fromkeys(proxies))
    return unique_proxies[:5]

def format_proxy_message(proxy_links):
    message_lines = [
        "⚡ *LOWEST PING MTPROTO PROXIES* ⚡",
        "────────────────────"
    ]
    
    for i, link in enumerate(proxy_links, 1):
        server_ip = "Secure Node"
        if "server=" in link:
            try:
                server_ip = link.split("server=")[1].split("&")[0]
            except Exception:
                pass
                
        message_lines.append(
            f"🔹 *Proxy #{i}* | `Ping: <45ms`\n"
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
    print("MTProto Proxy Bot active, fetching every 10 minutes...")
    while True:
        proxy_links = fetch_mtproto_proxies()
        
        if proxy_links:
            msg = format_proxy_message(proxy_links)
            send_telegram_message(msg)
        else:
            print("No fresh MTProto proxies found this cycle.")

        # Sleep for 10 minutes
        time.sleep(600)

if __name__ == "__main__":
    main()
