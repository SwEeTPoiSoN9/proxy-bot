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
    await update.message.reply_text("👋 Hello! I am your Proxy Bot. Use /proxy to get fresh proxies with connection buttons!")

async def get_proxy_data():
    # Fetching free proxies (Example API or source)
    try:
        response = requests.get("https://proxylist.geonode.com/api/proxy-list?limit=3&page=1&sort_by=lastChecked&sort_type=desc", timeout=10)
        data = response.json().get('data', [])
        proxies = []
        for item in data:
            ip = item.get('ip')
            port = item.get('port')
            protocols = item.get('protocols', ['http'])
            country = item.get('country', 'Unknown')
            proto = protocols[0] if protocols else 'http'
            
            # Format proxy link/details
            proxy_url = f"{proto}://{ip}:{port}"
            name = f"{proto.upper()} Proxy ({country})"
            proxies.append({"name": name, "url": proxy_url, "ip": ip, "port": port})
        return proxies
    except Exception as e:
        logging.error(f"Error fetching proxies: {e}")
        return []

async def proxy_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    proxies = await get_proxy_data()
    if not proxies:
        await update.message.reply_text("❌ Could not fetch proxies at the moment. Please try again later.")
        return

    for p in proxies:
        # Create an inline button to connect/open the proxy directly
        keyboard = [[InlineKeyboardButton("🔗 Connect Proxy", url=f"https://t.me/proxy?server={p['ip']}&port={p['port']}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message_text = (
            f"🛡 **{p['name']}**\n\n"
            f"🌐 **Server:** `{p['ip']}`\n"
            f"🔌 **Port:** `{p['port']}`\n\n"
            f"Tap the button below to connect instantly:"
        )
        
        await update.message.reply_text(message_text, reply_markup=reply_markup, parse_mode="Markdown")

def main():
    if not BOT_TOKEN:
        logging.error("No BOT_TOKEN provided!")
        return

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("proxy", proxy_command))

    logging.info("Bot is starting...")
    app.run_polling()

if __name__ == '__main__':
    main()
