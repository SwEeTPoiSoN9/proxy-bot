import os
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Setup logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Configuration with fallback
BOT_TOKEN = os.getenv("BOT_TOKEN")
group_id_str = os.getenv("GROUP_ID")
GROUP_ID = int(group_id_str) if group_id_str else -1004315498301

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hello! I send live, verified Telegram SOCKS5 proxies every hour!")

async def fetch_socks5_proxies(count=5):
    """Fetches high-quality SOCKS5 proxies explicitly formatted for Telegram."""
    try:
        # Fetching verified SOCKS5 proxies from ProxyScrape API
        url = "https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=protocolipport&format=json&protocol=socks5"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        raw_proxies = data.get('proxies', [])
        proxies = []
        
        for item in raw_proxies[:count]:
            ip = item.get('ip')
            port = item.get('port')
            country = item.get('ip_data', {}).get('country', 'Global')
            
            if ip and port:
                proxies.append({
                    "ip": ip,
                    "port": port,
                    "country": country,
                    "name": f"SOCKS5 Telegram Proxy ({country})"
                })
        return proxies
    except Exception as e:
        logging.error(f"Error fetching SOCKS5 proxies: {e}")
        return []

async def send_proxies_to_group(context: ContextTypes.DEFAULT_TYPE):
    target_chat_id = context.job.chat_id if (context.job and context.job.chat_id) else GROUP_ID
    proxies = await fetch_socks5_proxies(count=5)
    
    if not proxies:
        return

    await context.bot.send_message(
        chat_id=target_chat_id,
        text="⚡ **Fresh Telegram SOCKS5 Proxies (Hourly)** ⚡\n_All links pre-configured for Telegram instant connect!_",
        parse_mode="Markdown"
    )

    for p in proxies:
        # Proper Telegram SOCKS5 URL syntax (t.me/socks)
        connect_url = f"https://t.me/socks?server={p['ip']}&port={p['port']}"
        
        keyboard = [[InlineKeyboardButton("🔗 Connect SOCKS5 Proxy", url=connect_url)]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message_text = (
            f"🛡 **{p['name']}**\n"
            f"🌐 **Server:** `{p['ip']}`\n"
            f"🔌 **Port:** `{p['port']}`\n"
            f"📡 **Type:** SOCKS5\n\n"
            f"Tap below to connect:"
        )
        await context.bot.send_message(
            chat_id=target_chat_id,
            text=message_text,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

async def auto_post_job(context: ContextTypes.DEFAULT_TYPE):
    await send_proxies_to_group(context)

async def proxy_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_proxies_to_group(context)

def main():
    if not BOT_TOKEN:
        logging.error("No BOT_TOKEN provided!")
        return

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("proxy", proxy_command))

    # Schedule automatic posting every 1 hour (3600 seconds)
    if app.job_queue:
        app.job_queue.run_repeating(auto_post_job, interval=3600, first=5, chat_id=GROUP_ID)

    logging.info("Bot started successfully!")
    app.run_polling()

if __name__ == '__main__':
    main()
