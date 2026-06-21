from typing import List

def calculate_moving_average_forecast(history: List[float]) -> float:
    """
    Рассчитывает прогноз на основе простого скользящего среднего (SMA).
    Берет среднее значение последних точек и проецирует тренд.
    """
    if not history:
        return 0.0
        
    # Нам нужно как минимум 3 точки для определения тренда
    if len(history) < 3:
        return round(history[-1], 2)
        
    # 1. Считаем базовое среднее значение последних цен (окно из 5 элементов или меньше)
    window_size = min(5, len(history))
    recent_prices = history[-window_size:]
    sma = sum(recent_prices) / window_size
    
    # 2. Определяем направление тренда (куда идет цена в последнее время)
    # Вычитаем из последней цены предпоследнюю
    trend = history[-1] - history[-2]
    
    # 3. Финальный прогноз: среднее значение + поправка на текущий тренд
    predicted = sma + (trend * 0.5)
    
    return round(predicted, 2)
