"""
Budget forecasting service for StudentFlow - generates spending predictions and recommendations.
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any


class BudgetForecaster:
    """Generates budget forecasts and financial recommendations."""
    
    def __init__(self):
        """Initialize the forecaster."""
        pass
    
    def generate_soft_curve(
        self,
        current_balance: float,
        daily_avg: float,
        days_left: int,
        fixed_expenses: Dict[str, tuple],
        exam_mode: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Generate a smooth forecast curve for budget prediction.
        
        Args:
            current_balance: Current account balance
            daily_avg: Average daily expenses
            days_left: Number of days to forecast
            fixed_expenses: Dict of {name: (amount, day_offset)} for scheduled expenses
            exam_mode: If True, increases predicted expenses during exam period
            
        Returns:
            List of forecast points with day, date, expected/min/max values, and risk zone
        """
        # Base linear projection
        base_slope = -daily_avg
        
        # Build expense schedule from fixed expenses
        expenses_schedule = {}
        for exp_name, (amount, day_offset) in fixed_expenses.items():
            day_idx = min(day_offset, days_left - 1)
            expenses_schedule[day_idx] = expenses_schedule.get(day_idx, 0) + amount
        
        # Uncertainty factor (grows toward end of period)
        uncertainty_factor = 0.15  # ±15% at start, up to ±40% at end
        
        curve = []
        cumulative = current_balance
        
        for day in range(days_left + 1):
            # Deduct scheduled expenses
            if day in expenses_schedule:
                cumulative -= expenses_schedule[day]
            
            # Base expected value
            expected = cumulative + base_slope * day
            
            # Exam mode: increase expenses by 20-30% in last third of period
            if exam_mode and day >= days_left * 0.7:
                expected *= 0.85  # Reduce forecast by 15%
            
            # "Soft" uncertainty corridor (smooth expansion)
            uncertainty = uncertainty_factor * (1 + day / days_left)
            min_val = expected * (1 - uncertainty)
            max_val = expected * (1 + uncertainty * 0.6)  # Upper bound is narrower
            
            # Determine risk zone
            if expected > current_balance * 0.5:
                risk_zone = "green"
            elif expected > current_balance * 0.2:
                risk_zone = "yellow"
            else:
                risk_zone = "red"
            
            curve.append({
                "day": day,
                "date": (datetime.now() + timedelta(days=day)).strftime("%Y-%m-%d"),
                "expected": round(expected, 2),
                "min": round(max(0, min_val), 2),  # Don't go negative
                "max": round(max_val, 2),
                "risk_zone": risk_zone
            })
        
        return curve
    
    def get_recommendation(self, curve: List[Dict[str, Any]]) -> str:
        """
        Generate a text recommendation based on the forecast curve.
        
        Args:
            curve: Forecast curve from generate_soft_curve
            
        Returns:
            Recommendation string
        """
        if not curve:
            return "⚠️ Unable to generate recommendation - no forecast data available."
        
        last_point = curve[-1]
        risk_zone = last_point.get("risk_zone", "red")
        
        if risk_zone == "green":
            return "✅ Forecast is favorable. You can afford small additional expenses."
        elif risk_zone == "yellow":
            return "⚠️ Budget is tight. Consider reducing optional expenses by 10-15%."
        else:
            return "🔴 Risk of deficit. Consider part-time work or temporary savings on: entertainment, delivery."
