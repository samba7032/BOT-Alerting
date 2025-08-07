import yfinance as yf
import pandas as pd
import ta
import time
import asyncio
from telegram import Bot
from datetime import datetime, time as dtime

# === CONFIG ===
TELEGRAM_TOKEN = '8305784916:AAE2UP_4CxpYVHxfpD1yFBk8hi3uU-vd32I'
CHAT_ID = '1020815701'

SYMBOLS = [
    'TATAMOTORS.NS', 'SBIN.NS', 'IOC.NS', 'PNB.NS', 'YESBANK.NS', 'IRFC.NS',
    'SWIGGY.NS', 'PAYTM.NS', 'IDEA.NS', 'HINDCOPPER.NS'
]

# === Setup Telegram Bot ===
bot = Bot(token=TELEGRAM_TOKEN)


async def send_alert(message):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 📲 ALERT SENT: {message}")
    await bot.send_message(chat_id=CHAT_ID, text=message)


def is_market_open():
    now = datetime.now()
    current_time = now.time()
    current_day = now.weekday()  # Monday = 0, Sunday = 6

    # Check if it's a weekday (Mon–Fri)
    if current_day >= 5:
        return False

    # Check if current time is within market hours
    return dtime(9, 15) <= current_time <= dtime(15, 30)
    #return True


async def check_signal(symbol):
    try:
        data = yf.download(symbol,
                           interval='1m',
                           period='1d',
                           auto_adjust=True,
                           progress=False)
        data.dropna(inplace=True)

        close_prices = data['Close'].squeeze()
        rsi = ta.momentum.RSIIndicator(close=close_prices, window=14).rsi()
        last_rsi = rsi.iloc[-1]
        last_price = close_prices.iloc[-1]

        print(
            f"[{datetime.now().strftime('%H:%M:%S')}] {symbol} → RSI: {last_rsi:.2f}, Price: ₹{last_price:.2f}"
        )

        if last_rsi < 30:
            await send_alert(
                f"🚀 BUY Signal for {symbol}\nRSI: {last_rsi:.2f}, Price: ₹{last_price:.2f}"
            )

        elif last_rsi > 70:
            await send_alert(
                f"🔻 SELL Signal for {symbol}\nRSI: {last_rsi:.2f}, Price: ₹{last_price:.2f}"
            )

    except Exception as e:
        print(f"❌ Error for {symbol}: {e}")


async def main():
    print("📡 Running Stock Alert Bot... (Ctrl+C to stop)")
    # === TEST ALERT ===
    await send_alert("✅ Test Alert: Your Stock Bot is active and running!")
    if (is_market_open()):
        await send_alert("✅ Market Opened: Hurry Market is Live Now!")

    while True:
        if is_market_open():
            for symbol in SYMBOLS:
                await check_signal(symbol)
        else:
            print(
                f"[{datetime.now().strftime('%H:%M:%S')}] 🕒 Market closed. Waiting..."
            )

        await asyncio.sleep(60)  # Wait 1 minute before next check


# === RUN THE MAIN LOOP ===
if __name__ == "__main__":
    asyncio.run(main())

