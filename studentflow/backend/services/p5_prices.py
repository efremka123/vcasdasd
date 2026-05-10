"""
Pyaterochka price service for StudentFlow - fetches and caches grocery prices.
"""
import asyncio
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional


class P5PriceService:
    """Service for fetching and caching Pyaterochka store prices."""
    
    DEFAULT_BASKET_IDS = [
        "1001",  # Milk 3.2%, 1L
        "1045",  # Eggs C1, 10 pcs
        "2034",  # Wheat bread
        "3012",  # Pasta, 450g
        "4056",  # Chicken fillet, 1kg
        "5023",  # Seasonal vegetables
    ]
    
    MOCK_PRODUCTS = [
        {"id": "1001", "name": "Milk 3.2%, 1L", "price": 89.99, "unit": "pcs"},
        {"id": "1045", "name": "Eggs C1, 10 pcs", "price": 119.99, "unit": "pack"},
        {"id": "2034", "name": "Wheat bread", "price": 45.99, "unit": "pcs"},
        {"id": "3012", "name": "Pasta, 450g", "price": 69.99, "unit": "pack"},
        {"id": "4056", "name": "Chicken fillet, 1kg", "price": 299.99, "unit": "kg"},
        {"id": "5023", "name": "Seasonal vegetables", "price": 129.99, "unit": "kg"},
    ]
    
    def __init__(
        self,
        store_sap_code: str = "12345",
        cache_ttl_hours: int = 168,
        data_dir: Optional[Path] = None
    ):
        """
        Initialize the price service.
        
        Args:
            store_sap_code: Store SAP code for price lookup
            cache_ttl_hours: Cache time-to-live in hours
            data_dir: Directory for cache file storage
        """
        self.store_sap_code = store_sap_code
        self.cache_ttl = timedelta(hours=cache_ttl_hours)
        self.data_dir = data_dir or Path(__file__).parent.parent / "data"
        self.cache_file = self.data_dir / "p5_prices_cache.json"
        self.use_mock = os.environ.get("P5_MOCK_MODE", "true").lower() == "true"
    
    async def _fetch_fresh_prices(self) -> Dict[str, Any]:
        """Fetch fresh prices from Pyaterochka API."""
        if self.use_mock:
            print("ℹ️ Using mock data for Pyaterochka (P5_MOCK_MODE=true)")
            return self._create_mock_response()
        
        try:
            # Note: Actual API integration would go here
            # from pyaterochka_api import PyaterochkaAPI
            # async with PyaterochkaAPI() as api:
            #     products = await self._fetch_products_from_api(api)
            #     return self._create_response(products)
            print("⚠️ API integration not available, using mock data")
            return self._create_mock_response()
        except Exception as e:
            print(f"⚠️ Error fetching prices from API: {e}")
            return self._create_mock_response(fallback=True)
    
    def _create_mock_response(self, fallback: bool = False) -> Dict[str, Any]:
        """Create a mock response for demonstration."""
        now = datetime.now()
        return {
            "store_code": self.store_sap_code,
            "fetched_at": now.isoformat(),
            "products": self.MOCK_PRODUCTS,
            "basket_total": sum(p["price"] for p in self.MOCK_PRODUCTS),
            "mock": True,
            "fallback": fallback
        }
    
    def _is_cache_valid(self, cache: Dict[str, Any]) -> bool:
        """Check if cached data is still valid."""
        if not cache or "fetched_at" not in cache:
            return False
        
        try:
            fetched = datetime.fromisoformat(cache["fetched_at"])
            return datetime.now() - fetched < self.cache_ttl
        except (ValueError, TypeError):
            return False
    
    def _load_cache(self) -> Optional[Dict[str, Any]]:
        """Load cache from file if it exists."""
        try:
            with open(self.cache_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return None
    
    def _save_cache(self, data: Dict[str, Any]) -> None:
        """Save data to cache file."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        with open(self.cache_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    async def get_student_basket_total(self) -> Dict[str, Any]:
        """
        Get total price for student basket (from cache or fresh).
        
        Returns:
            Dictionary with source indicator and basket data
        """
        # Try to load from cache
        cache = self._load_cache()
        if cache and cache.get("store_code") == self.store_sap_code and self._is_cache_valid(cache):
            return {"source": "cache", **cache}
        
        # Fetch fresh data
        fresh_data = await self._fetch_fresh_prices()
        
        # Save to cache
        self._save_cache(fresh_data)
        
        return {"source": "fresh", **fresh_data}
