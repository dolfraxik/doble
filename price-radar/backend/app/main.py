from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import engine, Base, get_db, PriceHistory
from app.scheduler import scheduler

app = FastAPI(title="Price Radar API (Async)")

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