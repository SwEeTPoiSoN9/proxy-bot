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
    await update.message.reply_text("👋 Hello! I send low-ping Telegram MTProto proxies every hour!")

async def fetch_mtproto_proxies(count=5):
    """Fetches fast, low-latency MTProto proxies specifically optimized for Telegram."""
    try:
        # Pushes fresh MTProto list from Telegram proxy providers
        url = "https://raw.githubusercontent.com/SoliSpirit/mtproto/main/all_proxies.txt"
        response = requests.get(url, timeout=10)
        lines = [line.strip() for line in response.text.splitlines() if line.strip().startswith("tg://proxy")]
        
        proxies = []
        for line in lines[:count]:
            # Parsing tg://proxy?server=IP&port=PORT&secret=SECRET
            params = {}
            query_str = line.split("?")[1] if "?" in line else ""
            for pair in query_str.split("&"):
                if "=" in pair:
                    k, v = pair.split("=", 1)
                    params[k] = v
            
            server = params.get("server")
            port = params.get("port")
            secret = params.get("secret")
            
            if server and port and secret:
                proxies.append({
                    "server": server,
                    "port": port,
                    "secret": secret,
                    "raw_link": line
                })
        return proxies
    except Exception as e:
        logging.error(f"Error fetching MTProto proxies: {e}")
        return []

async def send_proxies_to_group(context: ContextTypes.DEFAULT_TYPE):
    target_chat_id = context.job.chat_id if (context.job and context.job.chat_id) else GROUP_ID
    proxies = await fetch_mtproto_proxies(count=5)
    
    if not proxies:
        return

    await context.bot.send_message(
        chat_id=target_chat_id,
        text="🚀 **Fast MTProto Telegram Proxies (Low Ping)** 🚀\n_Native FakeTLS proxies for instant connection speed._",
        parse_mode="Markdown"
    )

    for idx, p in enumerate(proxies, 1):
        # Web fallback link for mobile/desktop button actions
        web_link = f"https://t.me/proxy?server={p['server']}&port={p['port']}&secret={p['secret']}"
        
        keyboard = [[InlineKeyboardButton("⚡ Connect Fast MTProto", url=web_link)]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message_text = (
            f"⚡ **MTProto Proxy #{idx}**\n"
            f"🌐 **Server:** `{p['server']}`\n"
            f"🔌 **Port:** `{p['port']}`\n"
            f"🔑 **Secret:** `{p['secret'][:10]}...`\n\n"
            f"Tap below for instant low-ping connection:"
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
