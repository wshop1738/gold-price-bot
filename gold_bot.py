import os
import yfinance as yf
import datetime
import requests

TOKEN = os.getenv("8454322645:AAEZjSAqVYo3h_ZFR4qT5BdQX6CjDWeM67U")
CHAT_ID = os.getenv("-1005250443251")

def send_gold_price():
    try:
        gold = yf.Ticker("GC=F")
        data = gold.history(period="1d", interval="1m")
        
        if data.empty:
            message = "❌ មិនអាចទាញតម្លៃមាសបានទេ។"
        else:
            price_oz = data['Close'].iloc[-1]
            price_per_gram = price_oz / 31.1034768
            price_kilo = round(price_per_gram * 1000, 2)
            price_375g = round(price_per_gram * 3.75, 2)
            
            # Cambodia time +7
            utc_now = datetime.datetime.now(datetime.timezone.utc)
            local_now = utc_now + datetime.timedelta(hours=7)
            date_str = local_now.strftime("%d/%m/%y")
            hour12 = local_now.hour % 12 or 12
            period = "ព្រឹក" if local_now.hour < 12 else "យប់"
            time_str = f"ម៉ោង {hour12}:{local_now.minute:02d} {period}"
            
            message = f"""{date_str}
{time_str}

មាស​គីឡូ ${price_kilo:,.2f}
តម្លៃ 3.75 ក្រាម ${price_375g:,.2f}"""
        
        # Send message using Telegram API (no telebot needed)
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": message}
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            print("✅ Sent successfully!")
        else:
            print("❌ Telegram API error:", response.text)
            
    except Exception as e:
        print("❌ Error:", str(e))

if __name__ == "__main__":
    send_gold_price()
