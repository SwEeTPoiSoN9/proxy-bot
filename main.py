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
    await update.message.reply_text("👋 Hello! I am your Proxy Bot. I automatically share fresh proxies in the group every hour!")

async def fetch_proxies(count=5):
    try:
        url = f"https://proxylist.geonode.com/api/proxy-list?limit={count}&page=1&sort_by=lastChecked&sort_type=desc"
        response = requests.get(url, timeout=10)
        data = response.json().get('data', [])
        proxies = []
        for item in data:
            ip = item.get('ip')
            port = item.get('port')
            protocols = item.get('protocols', ['http'])
            country = item.get('country', 'Unknown')
            proto = protocols[0] if protocols else 'http'
            
            name = f"{proto.upper()} Proxy ({country})"
            proxies.append({"name": name, "ip": ip, "port": port, "proto": proto})
        return proxies
    except Exception as e:
        logging.error(f"Error fetching proxies: {e}")
        return []

async def send_proxies_to_group(context: ContextTypes.DEFAULT_TYPE):
    target_chat_id = context.job.chat_id if context.job and context.job.chat_id else GROUP_ID
    proxies = await fetch_proxies(count=5)
    
    if not proxies:
        return

    await context.bot.send_message(
        chat_id=target_chat_id,
        text="⚡ **Fresh Proxies Update (Hourly)** ⚡",
        parse_mode="Markdown"
    )

    for p in proxies:
        keyboard = [[InlineKeyboardButton("🔗 Connect Proxy", url=f"https://t.me/proxy?server={p['ip']}&port={p['port']}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message_text = (
            f"🛡 **{p['name']}**\n"
            f"🌐 **Server:** `{p['ip']}`\n"
            f"🔌 **Port:** `{p['port']}`\n\n"
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
        app.job_queue.run_repeating(auto_post_job, interval=3600, first=10, chat_id=GROUP_ID)

    logging.info("Bot started successfully!")
    app.run_polling()

if __name__ == '__main__':
    main()
