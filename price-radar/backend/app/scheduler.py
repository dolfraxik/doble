import httpx
import asyncio
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.database import AsyncSessionLocal, PriceHistory

async def fetch_crypto_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            if response.status_code == 200:
                data = response.json()
                btc_price = float(data["bitcoin"]["usd"])
                
                
                async with AsyncSessionLocal() as session:
                    async with session.begin():
                        new_price = PriceHistory(
                            ticker="btc",
                            price=btc_price,
                            timestamp=datetime.utcnow()
                        )
                        session.add(new_price)
                print(f"[{datetime.now()}] Успешно сохранена цена BTC: ${btc_price}")
            else:
                print(f"Ошибка API CoinGecko: {response.status_code}")
        except Exception as e:
            print(f"Ошибка при сборе данных: {e}")


scheduler = AsyncIOScheduler()


scheduler.add_job(fetch_crypto_price, "interval", minutes=1)