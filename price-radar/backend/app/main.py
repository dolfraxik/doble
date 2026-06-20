import httpx
from fastapi import FastAPI, Depends,HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import engine, Base, get_db, PriceHistory
from app.scheduler import scheduler

app = FastAPI(title="Price Radar API (Async)")

ML_SERVICE_URL = "http://127.0.0.1:8001/predict"

@app.get("/forecast/{ticker}")
async def get_price_forecast(ticker: str, db: AsyncSession = Depends(get_db)):
    # 1. Достаем последние 10 записей из базы данных
    result = await db.execute(
        select(PriceHistory)
        .where(PriceHistory.ticker == ticker.lower())
        .order_by(PriceHistory.timestamp.desc())
        .limit(10)
    )
    history_records = result.scalars().all()
    
    # Если данных слишком мало, модель не сможет сделать прогноз
    if len(history_records) < 3:
        raise HTTPException(
            status_code=400, 
            detail="Недостаточно данных в БД для прогноза. Подождите немного."
        )
    
    # 2. Переворачиваем массив, чтобы цены шли от старых к самым новым
    prices_list = [record.price for record in reversed(history_records)]
    
    # 3. Отправляем данные в ML-сервис напарника
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                ML_SERVICE_URL, 
                json={"history": prices_list},
                timeout=5.0 # чтобы бэкенд не завис, если у MLщика упадет сервер
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=502, detail="ML сервис вернул ошибку")
                
            ml_data = response.json()
            
            # 4. Возвращаем пользователю красивый ответ
            return {
                "ticker": ticker,
                "current_price": prices_list[-1],
                "predicted_next_price": ml_data.get("predicted_price"),
                "recommendation": ml_data.get("recommendation"),
                "based_on_points": len(prices_list)
            }
            
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="ML сервис недоступен")
@app.on_event("startup")
async def startup_event():
    # 1. Создаем таблицы в БД, если их нет
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # 2. Запускаем автоматический сборщик цен
    scheduler.start()
    print("Планировщик задач успешно запущен!")

@app.get("/")
def read_root():
    return {"status": "working", "message": "Welcome to Price Radar Async API"}

@app.get("/history/{ticker}")
async def get_price_history(ticker: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(PriceHistory)
        .where(PriceHistory.ticker == ticker.lower())
        .order_by(PriceHistory.timestamp.desc())
        .limit(20)
    )
    history = result.scalars().all()
    return {"ticker": ticker, "count": len(history), "data": history}