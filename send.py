import os
import telebot
import yfinance as yf
import datetime

# ==== CONFIG (from GitHub Secrets) ====
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not TOKEN:
    raise Exception("BOT_TOKEN secret is missing")
if not CHAT_ID:
    raise Exception("CHAT_ID secret is missing")

CHAT_ID = int(CHAT_ID)

bot = telebot.TeleBot(TOKEN)

# ==== FUNCTIONS ====

def get_gold_price_message():
    try:
        # Get gold price from Yahoo Finance
        gold = yf.Ticker("GC=F")
        data = gold.history(period="1d", interval="1m")

        # Fallback if no minute data
        if data.empty:
            data = gold.history(period="1d")

        if data.empty:
            return "❌ មិនអាចទាញតម្លៃមាសបានទេ។"

        # Price calculations
        price_oz = data['Close'].dropna().iloc[-1]
        price_per_gram = price_oz / 31.1034768
        price_375g = round(price_per_gram * 3.75, 2)

        # Cambodia time (UTC+7)
        now = datetime.datetime.utcnow() + datetime.timedelta(hours=7)
        date_str = now.strftime("%d/%m/%y")
        hour = now.hour % 12 or 12
        period = "ព្រឹក" if now.hour < 12 else "យប់"
        time_str = f"ម៉ោង {hour}:{now.minute:02d} {period}"

        # Format message
        message = f"""{date_str}
{time_str}
មាស​គីឡូ {price_375g}$"""
        return message

    except Exception as e:
        return f"❌ មានបញ្ហា: {str(e)}"


def send_gold_price():
    msg = get_gold_price_message()
    print("MESSAGE TO SEND:\n", msg)
    bot.send_message(CHAT_ID, msg)
    print("✅ Message sent successfully")


# ==== RUN SCRIPT ====
if __name__ == "__main__":
    send_gold_price() 
