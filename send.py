import os
import datetime
import time
import yfinance as yf
import telebot

# ===== ENV =====
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")  # 👈 your personal Telegram ID

if not TOKEN or not CHAT_ID:
    raise Exception("❌ BOT_TOKEN or CHAT_ID not set")

bot = telebot.TeleBot(TOKEN)

# ===== GET GOLD PRICE =====
def get_gold_price():
    try:
        gold = yf.Ticker("GC=F")
        data = gold.history(period="1d", interval="1m")

        if data.empty:
            raise Exception("No data from Yahoo")

        price_oz = data['Close'].iloc[-1]

        grams_per_oz = 31.1034768
        price_per_gram = price_oz / grams_per_oz

        price_375g = round(price_per_gram * 3.75, 2)

        return price_375g

    except Exception as e:
        raise Exception(f"Gold fetch error: {e}")


# ===== FORMAT =====
def format_message(price):
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=7)

    date_str = now.strftime("%d/%m/%y")

    hour = now.hour
    minute = now.minute

    hour12 = hour % 12 or 12
    period = "ព្រឹក" if hour < 12 else "យប់"

    time_str = f"ម៉ោង {hour12}:{minute:02d} {period}"

    return f"""{date_str}
{time_str}
មាសគីឡូ​ {price:,.2f}$"""


# ===== SEND WITH RETRY =====
def send_with_retry(message, retries=3):
    for attempt in range(1, retries + 1):
        try:
            bot.send_message(CHAT_ID, message)
            print(f"✅ Sent (attempt {attempt})")
            return True

        except Exception as e:
            print(f"⚠️ Attempt {attempt} failed: {e}")
            time.sleep(5)

    return False


# ===== ERROR ALERT =====
def notify_admin(error_text):
    if not ADMIN_CHAT_ID:
        print("⚠️ No ADMIN_CHAT_ID set")
        return

    try:
        bot.send_message(ADMIN_CHAT_ID, f"❌ Gold Bot Error:\n{error_text}")
        print("📢 Admin notified")

    except Exception as e:
        print("❌ Failed to notify admin:", e)


# ===== MAIN =====
def run():
    try:
        price = get_gold_price()
        message = format_message(price)

        success = send_with_retry(message)

        if not success:
            raise Exception("Failed after retries")

    except Exception as e:
        print("❌ ERROR:", e)
        notify_admin(str(e))


if __name__ == "__main__":
    run() 
