import asyncio
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import httpx
from app.database import AsyncSessionLocal, PriceHistory

scheduler = AsyncIOScheduler()

# Сопоставление ID в CoinGecko и коротких тикеров в нашей БД
TICKERS_MAP = {
    "bitcoin": "btc",
    "ethereum": "eth",
    "solana": "sol"
}

async def fetch_crypto_prices():
    coin_ids = ",".join(TICKERS_MAP.keys())
    url = f"https://coingecko.com{coin_ids}&vs_currencies=usd"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                
                async with AsyncSessionLocal() as db:
                    for coin_id, ticker in TICKERS_MAP.items():
                        if coin_id in data:
                            price = float(data[coin_id]["usd"])
                            
                            new_record = PriceHistory(ticker=ticker, price=price)
                            db.add(new_record)
                            
                    await db.commit()
                    print(f"[{datetime.now()}] Успешно обновлены цены для: BTC, ETH, SOL", flush=True)
            else:
                print(f"[{datetime.now()}] Ошибка API CoinGecko: {response.status_code}", flush=True)
        except Exception as e:
            print(f"[{datetime.now()}] Ошибка сети при сборе цен: {e}", flush=True)

def start_scheduler():
    scheduler.add_job(fetch_crypto_prices, "interval", minutes=1, id="crypto_job", replace_existing=True)
    scheduler.start()
    print("Планировщик задач мульти-тикерности успешно запущен!", flush=True)
