from flask import Flask
from threading import Thread
import telebot
import yfinance as yf
import schedule
import time
from datetime import datetime, timezone

# === YOUR SETTINGS ===
TOKEN = "8454322645:AAEZjSAqVYo3h_ZFR4qT5BdQX6CjDWeM67U"
CHAT_ID = -1005250443251   # ←←← CHANGE THIS to your NEW ID from Step 1
# =====================

bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

@app.route('/')
def home():
    return "🟡 Gold Price Bot is alive!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

Thread(target=run_flask).start()

def get_gold_price_message():
    try:
        gold = yf.Ticker("GC=F")
        data = gold.history(period="1d", interval="1m")
        if data.empty:
            return "❌ មិនអាចទាញតម្លៃមាសបានទេ។"
        
        price_oz = data['Close'].iloc[-1]
        price_per_gram = price_oz / 31.1034768
        price_kilo = round(price_per_gram * 1000, 2)
        price_375g = round(price_per_gram * 3.75, 2)
        
        utc_now = datetime.now(timezone.utc)
        local_now = utc_now + time.timedelta(hours=7)
        date_str = local_now.strftime("%d/%m/%y")
        hour12 = local_now.hour % 12 or 12
        period = "ព្រឹក" if local_now.hour < 12 else "យប់"
        time_str = f"ម៉ោង {hour12}:{local_now.minute:02d} {period}"
        
        return f"""{date_str}
{time_str}

មាស​គីឡូ ${price_kilo:,.2f}
តម្លៃ 3.75 ក្រាម ${price_375g:,.2f}"""
    except:
        return "❌ មានបញ្ហា សាកល្បងម្តងទៀត។"

def send_gold_update():
    message = get_gold_price_message()
    try:
        bot.send_message(CHAT_ID, message)
        print("✅ Sent successfully at", datetime.now(timezone.utc) + time.timedelta(hours=7))
    except Exception as e:
        print("❌ Telegram Error:", str(e))
        if "migrate_to_chat_id" in str(e).lower():
            print("🔄 Your group is still using old ID. Use @RawDataBot again to get the latest one.")

# Send first message now
send_gold_update()

# Every hour
schedule.every().hour.do(send_gold_update)

print("🤖 Bot started on Replit! Sending every hour...")

while True:
    schedule.run_pending()
    time.sleep(60)
