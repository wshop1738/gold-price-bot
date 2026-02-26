import os
import time
import traceback
from datetime import datetime

import telebot
import yfinance as yf
import pytz

# ================= CONFIG =================
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")  # your personal Telegram ID

bot = telebot.TeleBot(BOT_TOKEN)

# Cambodia timezone
TZ = pytz.timezone("Asia/Phnom_Penh")


# ================= TIME PERIOD =================
def get_khmer_time_period(hour):
    if 5 <= hour <= 10:
        return "ព្រឹក"
    elif 11 <= hour <= 13:
        return "ថ្ងៃ"
    elif 14 <= hour <= 15:
        return "រសៀល"
    elif 16 <= hour <= 17:
        return "ល្ងាច"
    else:
        return "យប់"


# ================= GOLD PRICE =================
def get_gold_price():
    """
    Get gold price per ounce from Yahoo Finance (XAUUSD)
    Then convert to your format safely
    """
    gold = yf.Ticker("XAUUSD=X")
    data = gold.history(period="1d")

    if data.empty:
        raise Exception("No gold data received")

    price_per_oz = float(data["Close"].iloc[-1])

    # 👉 Convert to your preferred value (example: Khmer market style)
    # You can adjust this formula if needed
    price_per_gram = price_per_oz / 31.1035
    price_per_kilo = price_per_gram * 1000

    # ✅ Prevent crazy number bug
    if price_per_kilo > 100000:
        price_per_kilo = price_per_kilo / 100  # fix scale issue

    return round(price_per_kilo, 2)


# ================= MESSAGE =================
def build_message():
    now = datetime.now(TZ)

    date_str = now.strftime("%y/%m/%d")
    time_str = now.strftime("%I:%M")
    period = get_khmer_time_period(now.hour)

    price = get_gold_price()

    msg = f"""📅 {date_str}
ម៉ោង {time_str} {period}
មាស​គីឡូ {price:,.2f}$"""

    return msg


# ================= SEND WITH RETRY =================
def send_with_retry(chat_id, message, retries=3):
    for attempt in range(retries):
        try:
            bot.send_message(chat_id, message)
            return True
        except Exception as e:
            time.sleep(5)

    return False


# ================= MAIN =================
def send_gold_price():
    try:
        msg = build_message()
        print("MESSAGE TO SEND:\n", msg)

        success = send_with_retry(CHAT_ID, msg)

        if not success:
            raise Exception("Failed after retries")

    except Exception as e:
        error_msg = f"❌ ERROR:\n{str(e)}\n\n{traceback.format_exc()}"
        print(error_msg)

        # ✅ Only notify admin (not spam group)
        if ADMIN_CHAT_ID:
            try:
                bot.send_message(ADMIN_CHAT_ID, error_msg[:4000])
            except:
                pass


# ================= RUN =================
if __name__ == "__main__":
    send_gold_price()
