import os
import logging
import requests
from datetime import time
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Safely load configuration from Railway variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = int(os.getenv("GROUP_ID"))

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Proxy Bot is running 24/7 on Railway!\n\n"
        "Commands:\n"
        "/proxy – Get free HTTP + SOCKS5\n"
        "/mtproto – Get free MTProto proxies\n"
        "/help – Help"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "This bot auto-posts fresh free proxies every day in the group.\n"
        "You can also request them anytime with /proxy or /mtproto."
    )

def fetch_http_socks():
    try:
        http = requests.get(
            "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
            timeout=15
        ).text.strip()
        
        socks5 = requests.get(
            "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks5&timeout=10000&country=all",
            timeout=15
        ).text.strip()
        return http, socks5
    except:
        return "", ""

def fetch_mtproto():
    sources = [
        "https://raw.githubusercontent.com/SoliSpirit/mtproto/master/all_proxies.txt",
        "https://raw.githubusercontent.com/ALIILAPRO/MTProtoProxy/main/mtproto.txt",
        "https://raw.githubusercontent.com/Surfboardv2ray/TGProto/main/proxies.txt",
    ]
    proxies = []
    for url in sources:
        try:
            data = requests.get(url, timeout=12).text
            for line in data.splitlines():
                line = line.strip()
                if "tg://proxy" in line or "t.me/proxy" in line:
                    proxies.append(line)
        except:
            continue
    return list(dict.fromkeys(proxies))[:20]

async def send_proxy_post(context: ContextTypes.DEFAULT_TYPE):
    http, socks5 = fetch_http_socks()
    mtproto = fetch_mtproto()

    text = (
        "🔥 **Fresh Free Proxies** 🔥\n\n"
        "📌 **HTTP Proxies:**\n"
        f"`{http[:1200]}`\n\n"
        "📌 **SOCKS5 Proxies:**\n"
        f"`{socks5[:1200]}`\n\n"
        "⚡ **MTProto Proxies (Telegram):**\n"
    )

    if mtproto:
        text += "\n".join(mtproto[:12])
    else:
        text += "No MTProto proxies available right now."

    text += "\n\n⚠️ Free proxies die fast. Request new ones anytime with /proxy or /mtproto"

    try:
        await context.bot.send_message(
            chat_id=GROUP_ID,
            text=text,
            parse_mode="Markdown",
            disable_web_page_preview=True
        )
    except Exception as e:
        logging.error(f"Failed to send daily post: {e}")

async def get_proxy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("Fetching proxies...")
    http, socks5 = fetch_http_socks()
    text = (
        "**HTTP Proxies:**\n"
        f"`{http[:1400]}`\n\n"
        "**SOCKS5 Proxies:**\n"
        f"`{socks5[:1400]}`"
    )
    await msg.edit_text(text, parse_mode="Markdown")

async def get_mtproto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("Fetching MTProto proxies...")
    proxies = fetch_mtproto()
    if not proxies:
        await msg.edit_text("No MTProto proxies found right now.")
        return
    text = "**Free MTProto Proxies:**\n\n" + "\n\n".join(proxies)
    await msg.edit_text(text, parse_mode="Markdown", disable_web_page_preview=True)

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("proxy", get_proxy))
    app.add_handler(CommandHandler("mtproto", get_mtproto))

    job_queue = app.job_queue
    job_queue.run_daily(send_proxy_post, time=time(hour=9, minute=0))
    job_queue.run_daily(send_proxy_post, time=time(hour=18, minute=0))

    print("Bot started with daily auto-posting...")
    app.run_polling()

if __name__ == "__main__":
    main()
