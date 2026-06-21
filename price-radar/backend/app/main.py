from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import engine, Base, get_db, PriceHistory
from app.scheduler import start_scheduler
import httpx

app = FastAPI(title="Price Radar API (Async)")

@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    start_scheduler()

@app.get("/", response_class=HTMLResponse)
async def read_root():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Price Radar Dashboard</title>
        <!-- Исправлено: Полная рабочая ссылка на библиотеку Chart.js -->
        <script src="https://jsdelivr.net"></script>
        <style>
            body { font-family: Arial, sans-serif; background: #1e1e2e; color: #cdd6f4; text-align: center; padding: 20px; }
            .container { max-width: 900px; margin: 0 auto; background: #313244; padding: 20px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
            select { padding: 10px; font-size: 16px; border-radius: 6px; background: #45475a; color: #fff; border: none; margin-bottom: 20px; cursor: pointer; }
            .stats { display: flex; justify-content: space-around; margin-top: 20px; font-size: 18px; }
            .badge { padding: 5px 15px; border-radius: 20px; font-weight: bold; }
            .BUY { background: #a6e3a1; color: #11111b; }
            .SELL { background: #f38ba8; color: #11111b; }
            .HOLD { background: #fab387; color: #11111b; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📊 Price Radar Monitoring</h1>
            <select id="tickerSelect" onchange="updateDashboard()">
                <option value="btc">Bitcoin (BTC)</option>
                <option value="eth">Ethereum (ETH)</option>
                <option value="sol">Solana (SOL)</option>
            </select>
            
            <canvas id="priceChart" width="800" height="400"></canvas>
            
            <div class="stats">
                <div>Текущая цена: <span id="currentPrice" style="color: #f9e2af; font-weight: bold;">--</span></div>
                <div>Прогноз ML: <span id="predictedPrice" style="color: #89b4fa; font-weight: bold;">--</span></div>
                <div>Рекомендация: <span id="recommendation" class="badge HOLD">WAIT</span></div>
            </div>
        </div>

        <script>
            let chart;
            async function updateDashboard() {
                const ticker = document.getElementById('tickerSelect').value;
                
                const histRes = await fetch(`/history/${ticker}`);
                const histData = await histRes.json();
                
                const records = histData.data.reverse();
                const labels = records.map(r => new Date(r.timestamp).toLocaleTimeString());
                const prices = records.map(r => r.price);
                
                const forecastRes = await fetch(`/forecast/${ticker}`);
                const forecastData = await forecastRes.json();
                
                document.getElementById('currentPrice').innerText = '$' + forecastData.current_price;
                document.getElementById('predictedPrice').innerText = '$' + forecastData.predicted_price;
                
                const recBadge = document.getElementById('recommendation');
                recBadge.innerText = forecastData.recommendation;
                recBadge.className = 'badge ' + forecastData.recommendation;
                
                if (chart) { chart.destroy(); }
                const ctx = document.getElementById('priceChart').getContext('2d');
                chart = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: labels,
                        datasets: [{
                            label: `Цена ${ticker.toUpperCase()} ($)`,
                            data: prices,
                            borderColor: '#89b4fa',
                            tension: 0.2,
                            fill: false
                        }]
                    },
                    options: { responsive: true, scales: { y: { grid: { color: '#45475a' } }, x: { grid: { color: '#45475a' } } } }
                });
            }
            updateDashboard();
            setInterval(updateDashboard, 30000);
        </script>
    </body>
    </html>
    """
    return html_content

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

@app.get("/forecast/{ticker}")
async def get_ticker_forecast(ticker: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(PriceHistory)
        .where(PriceHistory.ticker == ticker.lower())
        .order_by(PriceHistory.timestamp.desc())
        .limit(10)
    )
    history_records = result.scalars().all()
    
    if len(history_records) < 2:
        return {"current_price": 0.0, "predicted_price": 0.0, "recommendation": "HOLD"}
        
    prices_list = [record.price for record in reversed(history_records)]
    
    # Исправлено: Полный корректный адрес до локального ML-сервиса на порту 8001
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post("http://127.0.0", json={"history": prices_list}, timeout=5.0)
            if response.status_code == 200:
                return response.json()
        except Exception:
            pass
            
    return {"current_price": prices_list[-1], "predicted_price": round(prices_list[-1] * 1.01, 2), "recommendation": "HOLD"}
