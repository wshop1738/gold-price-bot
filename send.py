import telebot
import yfinance as yf
import os
import datetime

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))

bot = telebot.TeleBot(TOKEN)

def get_gold_price_message():
    try:
        gold = yf.Ticker("GC=F")
        data = gold.history(period="1d", interval="1m")

        if data.empty:
            data = gold.history(period="1d")

        if data.empty:
            return "❌ មិនអាចទាញតម្លៃមាសបានទេ។"

        price_oz = data['Close'].iloc[-1]
        price_per_gram = price_oz / 31.1034768
        price_375g = round(price_per_gram * 3.75, 2)

        now = datetime.datetime.utcnow() + datetime.timedelta(hours=7)

        date_str = now.strftime("%d/%m/%y")

        hour = now.hour % 12 or 12
        period = "ព្រឹក" if now.hour < 12 else "យប់"

        time_str = f"ម៉ោង {hour}:{now.minute:02d} {period}"

        return f"""{date_str}
{time_str}
មាស​គីឡូ {price_375g}$"""

    except Exception as e:
        return f"❌ មានបញ្ហា: {str(e)}"


def send():
    msg = get_gold_price_message()
    bot.send_message(CHAT_ID, msg)

send()
