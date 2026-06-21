from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from app.model import calculate_moving_average_forecast

app = FastAPI(title="Price Radar ML Service")

class PredictRequest(BaseModel):
    history: List[float]

@app.get("/")
def read_root():
    return {"status": "online", "service": "ML Moving Average Predictor"}

@app.post("/predict")
def predict(data: PredictRequest):
    if not data.history:
        return {"current_price": 0.0, "predicted_price": 0.0, "recommendation": "HOLD", "error": "History is empty"}
        
    last_price = data.history[-1]
    
    # Вызываем нашу математическую модель
    predicted_price = calculate_moving_average_forecast(data.history)
    
    # Логика выдачи рекомендаций на основе математики
    # Если прогноз выше текущей цены более чем на 0.05% -> Покупаем
    if predicted_price > last_price * 1.0005:
        recommendation = "BUY"
    # Если прогноз ниже текущей цены более чем на 0.05% -> Продаем
    elif predicted_price < last_price * 0.9995:
        recommendation = "SELL"
    else:
        recommendation = "HOLD"
        
    return {
        "current_price": last_price,
        "predicted_price": predicted_price,
        "recommendation": recommendation
    }
