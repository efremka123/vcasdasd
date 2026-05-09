from datetime import datetime, timedelta
import numpy as np
from scipy import stats


class BudgetForecaster:
    def __init__(self, db_connection):
        self.db = db_connection
    
    def calculate_daily_average(self, category: str, days: int = 30) -> float:
        """Считает средние траты по категории за период"""
        query = """
            SELECT amount, date FROM transactions 
            WHERE category = ? AND date >= date('now', ?) AND type = 'expense'
        """
        rows = self.db.execute(query, (category, f"-{days} days")).fetchall()
        if not rows:
            return 0.0
        total = sum(r[0] for r in rows)
        return total / days
    
    def generate_soft_curve(self, current_balance: float, 
                           daily_avg: float, 
                           days_left: int,
                           fixed_expenses: dict,
                           exam_mode: bool = False) -> list[dict]:
        """
        Генерирует данные для плавного графика прогноза.
        Возвращает список точек {day: int, min: float, expected: float, max: float}
        """
        # Базовый линейный прогноз
        base_slope = -daily_avg
        
        # Добавляем фиксированные расходы в нужные дни
        expenses_schedule = {}
        for exp_name, (amount, day_offset) in fixed_expenses.items():
            day_idx = min(day_offset, days_left - 1)
            expenses_schedule[day_idx] = expenses_schedule.get(day_idx, 0) + amount
        
        # Коэффициент неопределённости (растёт к концу периода)
        uncertainty_factor = 0.15  # ±15% на начало, до ±40% к концу
        
        curve = []
        cumulative = current_balance
        
        for day in range(days_left + 1):
            # Списываем плановые расходы
            if day in expenses_schedule:
                cumulative -= expenses_schedule[day]
            
            # Базовое ожидаемое значение
            expected = cumulative + base_slope * day
            
            # Режим сессии: увеличиваем траты на 20-30%
            if exam_mode and day >= days_left * 0.7:  # последняя треть периода
                expected *= 0.85  # уменьшаем прогноз на 15%
            
            # "Мягкий" коридор неопределённости (плавное расширение)
            uncertainty = uncertainty_factor * (1 + day / days_left)
            min_val = expected * (1 - uncertainty)
            max_val = expected * (1 + uncertainty * 0.6)  # верхняя граница уже
            
            curve.append({
                "day": day,
                "date": (datetime.now() + timedelta(days=day)).strftime("%Y-%m-%d"),
                "expected": round(expected, 2),
                "min": round(max(0, min_val), 2),  # не уходим в отрицательные значения
                "max": round(max_val, 2),
                "risk_zone": "green" if expected > current_balance * 0.5 
                            else "yellow" if expected > current_balance * 0.2 
                            else "red"
            })
        
        return curve
    
    def get_recommendation(self, curve: list[dict]) -> str:
        """Генерирует текстовую рекомендацию на основе прогноза"""
        last_point = curve[-1]
        if last_point["risk_zone"] == "green":
            return "✅ Прогноз благоприятный. Можно позволить небольшие дополнительные траты."
        elif last_point["risk_zone"] == "yellow":
            return "⚠️ Бюджет напряжённый. Рекомендуем сократить необязательные расходы на 10-15%."
        else:
            return "🔴 Риск дефицита. Рассмотрите подработку или временную экономию на категориях: развлечения, доставка."
