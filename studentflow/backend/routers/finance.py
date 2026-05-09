from fastapi import APIRouter, Query, HTTPException
from typing import Dict, Any
import json
from pathlib import Path
from datetime import datetime

from models.database import get_db_connection
from services.forecast import BudgetForecaster


router = APIRouter(prefix="/api", tags=["forecast", "balance", "prices"])

DATA_DIR = Path(__file__).parent.parent / "data"


@router.get("/balance/current")
def get_current_balance():
    """Получить текущий баланс пользователя"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            COALESCE(SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END), 0) as total_income,
            COALESCE(SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END), 0) as total_expense
        FROM transactions
    """)
    
    row = cursor.fetchone()
    conn.close()
    
    balance = row["total_income"] - row["total_expense"]
    
    return {
        "balance": round(balance, 2),
        "total_income": round(row["total_income"], 2),
        "total_expense": round(row["total_expense"], 2)
    }


@router.get("/forecast")
def get_forecast(days: int = Query(default=30, ge=1, le=90)):
    """Получить прогноз бюджета на указанное количество дней"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Получаем текущий баланс
    cursor.execute("""
        SELECT 
            COALESCE(SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END), 0) -
            COALESCE(SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END), 0) as balance
        FROM transactions
    """)
    current_balance = cursor.fetchone()["balance"]
    
    # Считаем средние дневные траты
    cursor.execute("""
        SELECT AVG(amount) as avg_expense
        FROM transactions
        WHERE type = 'expense' AND date >= date('now', '-30 days')
    """)
    row = cursor.fetchone()
    daily_avg = row["avg_expense"] if row["avg_expense"] else 0
    
    # Получаем настройки (режим сессии)
    cursor.execute("SELECT value FROM user_settings WHERE key = 'exam_mode'")
    exam_row = cursor.fetchone()
    exam_mode = False
    if exam_row:
        try:
            exam_mode = json.loads(exam_row["value"])
        except:
            pass
    
    conn.close()
    
    # Генерируем прогноз
    forecaster = BudgetForecaster(conn)
    
    # Фиксированные расходы (пример: подписки, интернет)
    fixed_expenses = {
        "internet": (500, 10),  # 500₽ через 10 дней
        "subscription": (299, 20)  # 299₽ через 20 дней
    }
    
    curve = forecaster.generate_soft_curve(
        current_balance=current_balance,
        daily_avg=daily_avg,
        days_left=days,
        fixed_expenses=fixed_expenses,
        exam_mode=exam_mode
    )
    
    recommendation = forecaster.get_recommendation(curve)
    
    # Получаем внешние цены
    transport_prices = get_transport_prices_sync()
    p5_prices = get_p5_prices_sync()
    
    return {
        "current_balance": round(current_balance, 2),
        "daily_avg_expense": round(daily_avg, 2),
        "exam_mode": exam_mode,
        "curve": curve,
        "recommendation": recommendation,
        "external_prices": {
            "transport": transport_prices,
            "p5_basket": p5_prices
        }
    }


def get_transport_prices_sync() -> Dict[str, Any]:
    """Синхронная обёртка для получения тарифов транспорта"""
    transport_file = DATA_DIR / "transport_prices.json"
    
    if not transport_file.exists():
        return {"error": "Файл с тарифами не найден"}
    
    with open(transport_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Проверяем, не пора ли обновить
    next_check = datetime.strptime(data["meta"]["next_check"], "%Y-%m-%d")
    needs_update = datetime.now() > next_check
    
    return {
        "troika_wallet": data["troika"]["wallet"],
        "student_metro_monthly": data["student_benefits"]["metro_monthly"],
        "student_bus_monthly": data["student_benefits"]["bus_monthly"],
        "student_combined_monthly": data["student_benefits"]["combined_monthly"],
        "needs_update": needs_update,
        "last_updated": data["meta"]["last_updated"]
    }


def get_p5_prices_sync() -> Dict[str, Any]:
    """Синхронная обёртка для получения цен Пятёрочки (из кэша)"""
    cache_file = DATA_DIR / "p5_prices_cache.json"
    
    if not cache_file.exists():
        return {
            "total": 0,
            "source": "no_cache",
            "message": "Кэш цен ещё не создан"
        }
    
    with open(cache_file, "r", encoding="utf-8") as f:
        cache = json.load(f)
    
    return {
        "total": cache.get("basket_total", 0),
        "source": cache.get("source", "cache"),
        "fetched_at": cache.get("fetched_at", ""),
        "products_count": len(cache.get("products", []))
    }


@router.get("/prices/transport")
def get_transport_prices():
    """Получить актуальные тарифы транспорта Москвы"""
    return get_transport_prices_sync()


@router.get("/prices/p5/basket")
def get_p5_basket_prices():
    """Получить сумму базовой продуктовой корзины Пятёрочки"""
    return get_p5_prices_sync()


@router.post("/prices/p5/basket/refresh")
async def refresh_p5_basket_prices():
    """Обновить кэш цен Пятёрочки (асинхронно)"""
    from services.p5_prices import P5PriceService
    
    service = P5PriceService(store_sap_code="12345")
    data = await service.get_student_basket_total()
    
    return {
        "message": "Кэш цен обновлён",
        **data
    }


@router.post("/settings/exam-mode")
def set_exam_mode(enabled: bool = Query(...)):
    """Включить/выключить режим сессии"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT OR REPLACE INTO user_settings (key, value)
        VALUES ('exam_mode', ?)
    """, (json.dumps(enabled),))
    
    conn.commit()
    conn.close()
    
    return {
        "exam_mode": enabled,
        "message": "Режим сессии включён 🎓" if enabled else "Режим сессии выключен"
    }
