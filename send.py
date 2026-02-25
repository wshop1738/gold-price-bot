import os
import datetime
import yfinance as yf
import telebot

# === ENV VARIABLES ===
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not TOKEN or not CHAT_ID:
    raise Exception("❌ BOT_TOKEN or CHAT_ID not set")

bot = telebot.TeleBot(TOKEN)

def get_gold_price():
    try:
        gold = yf.Ticker("GC=F")
        data = gold.history(period="1d", interval="1m")

        if data.empty:
            print("❌ No data from Yahoo Finance")
            return None

        price_oz = data['Close'].iloc[-1]

        grams_per_oz = 31.1034768
        price_per_gram = price_oz / grams_per_oz

        price_kilo = round(price_per_gram * 1000, 2)
        price_375g = round(price_per_gram * 3.75, 2)

        return price_kilo, price_375g

    except Exception as e:
        print("❌ Error getting gold price:", e)
        return None


def format_message(price_kilo, price_375g):
    # Cambodia time (UTC+7)
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=7)

    date_str = now.strftime("%d/%m/%y")

    hour = now.hour
    minute = now.minute

    hour12 = hour % 12
    if hour12 == 0:
        hour12 = 12

    period = "ព្រឹក" if hour < 12 else "យប់"

    time_str = f"ម៉ោង {hour12}:{minute:02d} {period}"

    msg = f"""{date_str}
{time_str}
មាស​គីឡូ {price_kilo:,.2f}$"""

    return msg


def send_gold_price():
    print("🚀 Running gold price bot...")

    result = get_gold_price()

    if not result:
        print("❌ Skip sending (no data)")
        return

    price_kilo, price_375g = result

    msg = format_message(price_kilo, price_375g)

    print("📩 MESSAGE:")
    print(msg)

    try:
        bot.send_message(chat_id=CHAT_ID, text=msg)
        print("✅ Sent successfully")

    except Exception as e:
        print("❌ Telegram send error:", e)


if __name__ == "__main__":
    send_gold_price()
