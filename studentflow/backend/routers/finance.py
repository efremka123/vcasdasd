"""
Finance management endpoints for StudentFlow API - balance, forecasting, and price tracking.
"""
from fastapi import APIRouter, Query, HTTPException
from typing import Dict, Any, List
import json
from pathlib import Path
from datetime import datetime

from backend.models.database import get_db_connection
from backend.services.forecast import BudgetForecaster


router = APIRouter(prefix="/api", tags=["forecast", "balance", "prices"])

# Configuration
DATA_DIR = Path(__file__).parent.parent / "data"
DEFAULT_FIXED_EXPENSES = {
    "internet": (500, 10),      # 500₽ in 10 days
    "subscription": (299, 20)   # 299₽ in 20 days
}


class PriceService:
    """Service for retrieving price information from various sources."""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
    
    def get_transport_prices(self) -> Dict[str, Any]:
        """Get Moscow transport tariff prices."""
        transport_file = self.data_dir / "transport_prices.json"
        
        if not transport_file.exists():
            raise HTTPException(status_code=404, detail="Transport prices file not found")
        
        with open(transport_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Check if update is needed
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
    
    def get_p5_basket_prices(self) -> Dict[str, Any]:
        """Get Pyaterochka basket prices from cache."""
        cache_file = self.data_dir / "p5_prices_cache.json"
        
        if not cache_file.exists():
            return {
                "total": 0,
                "source": "no_cache",
                "message": "Price cache not yet created"
            }
        
        with open(cache_file, "r", encoding="utf-8") as f:
            cache = json.load(f)
        
        return {
            "total": cache.get("basket_total", 0),
            "source": cache.get("source", "cache"),
            "fetched_at": cache.get("fetched_at", ""),
            "products_count": len(cache.get("products", []))
        }


# Initialize price service
price_service = PriceService(DATA_DIR)


@router.get("/balance/current")
def get_current_balance():
    """Get current user balance."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                COALESCE(SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END), 0) as total_income,
                COALESCE(SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END), 0) as total_expense
            FROM transactions
        """)
        
        row = cursor.fetchone()
        balance = row["total_income"] - row["total_expense"]
        
        return {
            "balance": round(balance, 2),
            "total_income": round(row["total_income"], 2),
            "total_expense": round(row["total_expense"], 2)
        }
    finally:
        conn.close()


@router.get("/forecast")
def get_forecast(days: int = Query(default=30, ge=1, le=90)):
    """Get budget forecast for specified number of days."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Get current balance
        cursor.execute("""
            SELECT 
                COALESCE(SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END), 0) -
                COALESCE(SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END), 0) as balance
            FROM transactions
        """)
        current_balance = cursor.fetchone()["balance"]
        
        # Calculate average daily expenses
        cursor.execute("""
            SELECT AVG(amount) as avg_expense
            FROM transactions
            WHERE type = 'expense' AND date >= date('now', '-30 days')
        """)
        row = cursor.fetchone()
        daily_avg = row["avg_expense"] if row["avg_expense"] else 0
        
        # Get exam mode setting
        cursor.execute("SELECT value FROM user_settings WHERE key = 'exam_mode'")
        exam_row = cursor.fetchone()
        exam_mode = False
        if exam_row:
            try:
                exam_mode = json.loads(exam_row["value"])
            except json.JSONDecodeError:
                pass
        
        # Generate forecast
        forecaster = BudgetForecaster()
        curve = forecaster.generate_soft_curve(
            current_balance=current_balance,
            daily_avg=daily_avg,
            days_left=days,
            fixed_expenses=DEFAULT_FIXED_EXPENSES,
            exam_mode=exam_mode
        )
        
        recommendation = forecaster.get_recommendation(curve)
        
        # Get external prices
        transport_prices = price_service.get_transport_prices()
        p5_prices = price_service.get_p5_basket_prices()
        
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
    finally:
        conn.close()


@router.get("/prices/transport")
def get_transport_prices():
    """Get current Moscow transport tariffs."""
    return price_service.get_transport_prices()


@router.get("/prices/p5/basket")
def get_p5_basket_prices():
    """Get Pyaterochka basic basket prices."""
    return price_service.get_p5_basket_prices()


@router.post("/prices/p5/basket/refresh")
async def refresh_p5_basket_prices():
    """Refresh Pyaterochka price cache (asynchronously)."""
    from backend.services.p5_prices import P5PriceService
    
    service = P5PriceService(store_sap_code="12345")
    data = await service.get_student_basket_total()
    
    return {
        "message": "Price cache refreshed successfully",
        **data
    }


@router.post("/settings/exam-mode")
def set_exam_mode(enabled: bool = Query(...)):
    """Enable or disable exam mode."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO user_settings (key, value)
            VALUES ('exam_mode', ?)
        """, (json.dumps(enabled),))
        
        conn.commit()
        
        return {
            "exam_mode": enabled,
            "message": "Exam mode enabled 🎓" if enabled else "Exam mode disabled"
        }
    finally:
        conn.close()
