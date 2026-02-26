import os
import time
import traceback
from datetime import datetime
import pytz
import yfinance as yf
import telebot

# ================= CONFIG =================
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")  # personal chat ID (private)
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")  # optional for error alerts

if not BOT_TOKEN or not CHAT_ID:
    raise Exception("BOT_TOKEN or CHAT_ID not set!")

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
    Convert to 3.75 gram price
    """
    try:
        gold = yf.Ticker("XAUUSD=X")
        data = gold.history(period="1d")

        if data.empty:
            raise Exception("No gold data received")

        price_per_oz = float(data["Close"].iloc[-1])
        price_per_gram = price_per_oz / 31.1035
        price_375g = round(price_per_gram * 3.75, 2)

        return price_375g

    except Exception as e:
        raise Exception(f"Gold fetch error: {e}")


# ================= BUILD MESSAGE =================
def build_message():
    now = datetime.now(TZ)
    date_str = now.strftime("%y/%m/%d")
    time_str = now.strftime("%I:%M")
    period = get_khmer_time_period(now.hour)

    price = get_gold_price()
    message = f"""📅 {date_str}
ម៉ោង {time_str} {period}
មាស 3.75ក្រាម {price:,.2f}$"""
    return message


# ================= SEND WITH RETRY =================
def send_with_retry(chat_id, message, retries=3):
    for attempt in range(1, retries + 1):
        try:
            bot.send_message(chat_id, message)
            print(f"✅ Sent successfully (attempt {attempt})")
            return True
        except Exception as e:
            print(f"⚠️ Attempt {attempt} failed: {e}")
            time.sleep(5)
    return False


# ================= ERROR ALERT =================
def notify_admin(error_text):
    if ADMIN_CHAT_ID:
        try:
            bot.send_message(ADMIN_CHAT_ID, f"❌ Gold Bot Error:\n{error_text}"[:4000])
            print("📢 Admin notified")
        except Exception as e:
            print(f"❌ Failed to notify admin: {e}")


# ================= MAIN =================
def main():
    try:
        msg = build_message()
        print("MESSAGE TO SEND:\n", msg)

        success = send_with_retry(CHAT_ID, msg)
        if not success:
            raise Exception("Failed to send after retries")

    except Exception as e:
        error_msg = f"{str(e)}\n\n{traceback.format_exc()}"
        print(error_msg)
        notify_admin(error_msg)


if __name__ == "__main__":
    main()
