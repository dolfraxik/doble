from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI(title="Price Radar ML Service")

# Описываем структуру входящих данных
class PredictRequest(BaseModel):
    history: List[float]

@app.post("/predict")
def predict(data: PredictRequest):
    # Пока модель обучается, делаем простую заглушку (mock):
    # Берем последнюю цену и как будто предсказываем рост на 1.5%
    last_price = data.history[-1]
    predicted_price = round(last_price * 1.015, 2)
    
    return {
        "predicted_price": predicted_price,
        "recommendation": "BUY"  # Или "SELL", если бы цена падала
    }