import os
import yfinance as yf
import pandas as pd
import ta
import asyncio
from telegram.ext import ApplicationBuilder
from telegram.constants import ParseMode
from datetime import datetime, time as dtime
from zoneinfo import ZoneInfo  # For IST time zone support (Python 3.9+)

# === Load from Railway Environment Variables ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# === Your Stock Symbols ===
SYMBOLS = [
    'TATAMOTORS.NS', 'SBIN.NS', 'IOC.NS', 'PNB.NS', 'YESBANK.NS',
    'IRFC.NS', 'SWIGGY.NS', 'PAYTM.NS', 'IDEA.NS', 'HINDCOPPER.NS'
]

app = None  # Telegram app will be created in main()

# === Function: Send Telegram Message ===
async def send_alert(message):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 📲 ALERT SENT: {message}")
    await app.bot.send_message(chat_id=CHAT_ID, text=message, parse_mode=ParseMode.HTML)

# === Function: Check if Indian Market is Open ===
def is_market_open():
    now = datetime.now(ZoneInfo("Asia/Kolkata"))
    current_time = now.time()
    current_day = now.weekday()
    print(f"🕒 Current IST time: {now.strftime('%Y-%m-%d %H:%M:%S')} (Weekday: {current_day})")
    return current_day < 5 and dtime(9, 15) <= current_time <= dtime(15, 30)

# === Function: Check RSI Signal for Stock ===
async def check_signal(symbol):
    try:
        data = yf.download(symbol, interval='1m', period='1d', auto_adjust=True, progress=False)
        data.dropna(inplace=True)

        close_prices = data['Close'].squeeze()
        rsi = ta.momentum.RSIIndicator(close=close_prices, window=14).rsi()
        last_rsi = rsi.iloc[-1]
        last_price = close_prices.iloc[-1]

        print(f"[{datetime.now().strftime('%H:%M:%S')}] {symbol} → RSI: {last_rsi:.2f}, Price: ₹{last_price:.2f}")

        if last_rsi < 30:
            await send_alert(f"🚀 <b>BUY Signal</b> for {symbol}\nRSI: {last_rsi:.2f}, Price: ₹{last_price:.2f}")
        elif last_rsi > 70:
            await send_alert(f"🔻 <b>SELL Signal</b> for {symbol}\nRSI: {last_rsi:.2f}, Price: ₹{last_price:.2f}")

    except Exception as e:
        print(f"❌ Error for {symbol}: {e}")

# === Main Function ===
async def main():
    global app
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    print("📡 Running Stock Alert Bot...")
    await send_alert("✅ Test Alert: Bot is active and running!")

    if is_market_open():
        await send_alert("✅ Market Opened: Hurry Market is Live Now!")
    else:
        await send_alert("❌ Market is currently closed.")

    while True:
        if is_market_open():
            for symbol in SYMBOLS:
                await check_signal(symbol)
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 🕒 Market closed. Waiting...")

        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())

