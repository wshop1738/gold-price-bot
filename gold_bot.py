import telebot
import yfinance as yf
import schedule
import time
import os
import datetime

# === Get from Render Environment Variables ===
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))

bot = telebot.TeleBot(TOKEN)

def get_gold_price_message():
    try:
        # Get live gold price (USD per ounce)
        gold = yf.Ticker("GC=F")
        data = gold.history(period="1d", interval="1m")
        
        if data.empty:
            return "❌ មិនអាចទាញតម្លៃមាសបានទេ។"
        
        price_oz = data['Close'].iloc[-1]
        grams_per_oz = 31.1034768
        price_per_gram = price_oz / grams_per_oz
        
        price_kilo = round(price_per_gram * 1000, 2)   # 1 គីឡូ
        price_375g = round(price_per_gram * 3.75, 2)   # 3.75 ក្រាម
        
        # Cambodia time (+7)
        utc_now = datetime.datetime.utcnow()
        local_now = utc_now + datetime.timedelta(hours=7)
        
        date_str = local_now.strftime("%d/%m/%y")
        
        hour12 = local_now.hour % 12
        if hour12 == 0:
            hour12 = 12
        period = "ព្រឹក" if local_now.hour < 12 else "យប់"
        time_str = f"ម៉ោង {hour12}:{local_now.minute:02d} {period}"
        
        message = f"""{date_str}
{time_str}

មាស​គីឡូ ${price_kilo:,.2f}
តម្លៃ 3.75 ក្រាម ${price_375g:,.2f}"""
        
        return message
        
    except Exception as e:
        return f"❌ មានបញ្ហា: {str(e)}"

def send_gold_update():
    message = get_gold_price_message()
    try:
        bot.send_message(CHAT_ID, message)
        print(f"✅ បានផ្ញើ នៅ {datetime.datetime.utcnow() + datetime.timedelta(hours=7)}")
    except Exception as e:
        print(f"❌ ផ្ញើមិនបាន: {e}")

# Send immediately when start
send_gold_update()

# Send every 1 hour
schedule.every().hour.do(send_gold_update)

print("🤖 Gold Price Bot ដំណើរការ! ផ្ញើរៀងរាល់ម៉ោង...")

while True:
    schedule.run_pending()
    time.sleep(60)
