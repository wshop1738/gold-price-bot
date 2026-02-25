import os
import telebot
import yfinance as yf
import datetime

TOKEN = os.getenv("8454322645:AAEZjSAqVYo3h_ZFR4qT5BdQX6CjDWeM67U")
CHAT_ID = int(os.getenv("-1005250443251"))

bot = telebot.TeleBot(TOKEN)

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
        
        # Cambodia time (+7)
        utc_now = datetime.datetime.now(datetime.timezone.utc)
        local_now = utc_now + datetime.timedelta(hours=7)
        date_str = local_now.strftime("%d/%m/%y")
        hour12 = local_now.hour % 12 or 12
        period = "ព្រឹក" if local_now.hour < 12 else "យប់"
        time_str = f"ម៉ោង {hour12}:{local_now.minute:02d} {period}"
        
        return f"""{date_str}
{time_str}

មាស​គីឡូ ${price_kilo:,.2f}
តម្លៃ 3.75 ក្រាម ${price_375g:,.2f}"""
    except Exception as e:
        return f"❌ មានបញ្ហា: {str(e)}"

if __name__ == "__main__":
    message = get_gold_price_message()
    try:
        bot.send_message(CHAT_ID, message)
        print("✅ ផ្ញើបានជោគជ័យនៅ", datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=7))
    except Exception as e:
        print("❌ ផ្ញើមិនបាន:", str(e))
