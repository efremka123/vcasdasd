from pyaterochka_api import PyaterochkaAPI
import asyncio
import json
from datetime import datetime, timedelta


class P5PriceService:
    def __init__(self, store_sap_code: str, cache_ttl_hours: int = 168):
        self.store_sap_code = store_sap_code  # ID конкретного магазина
        self.cache_ttl = timedelta(hours=cache_ttl_hours)
        self.cache_file = "data/p5_prices_cache.json"
    
    async def _fetch_fresh_prices(self) -> dict:
        """Получает актуальные цены из API Пятёрочки"""
        async with PyaterochkaAPI() as api:
            # Базовая продуктовая корзина студента
            student_basket_ids = [
                "1001",  # Молоко 3.2%, 1л
                "1045",  # Яйца С1, 10 шт
                "2034",  # Хлеб пшеничный
                "3012",  # Макароны, 450г
                "4056",  # Куриное филе, 1кг
                "5023",  # Овощи сезонные (усреднено)
            ]
            
            products = []
            for prod_id in student_basket_ids:
                try:
                    info = await api.Product.info(prod_id, self.store_sap_code)
                    products.append({
                        "id": prod_id,
                        "name": info.get("name"),
                        "price": info.get("price", 0),
                        "unit": info.get("unit", "шт"),
                        "fetched_at": datetime.now().isoformat()
                    })
                except Exception as e:
                    print(f"⚠️ Не удалось получить товар {prod_id}: {e}")
                    continue
            
            return {
                "store_code": self.store_sap_code,
                "fetched_at": datetime.now().isoformat(),
                "products": products,
                "basket_total": sum(p["price"] for p in products)
            }
    
    def _is_cache_valid(self, cache: dict) -> bool:
        """Проверяет, не устарел ли кэш"""
        if not cache:
            return False
        fetched = datetime.fromisoformat(cache["fetched_at"])
        return datetime.now() - fetched < self.cache_ttl
    
    async def get_student_basket_total(self) -> dict:
        """Возвращает сумму базовой корзины (из кэша или свежую)"""
        # Пробуем прочитать кэш
        try:
            with open(self.cache_file, "r", encoding="utf-8") as f:
                cache = json.load(f)
                if cache.get("store_code") == self.store_sap_code and self._is_cache_valid(cache):
                    return {"source": "cache", **cache}
        except FileNotFoundError:
            pass
        
        # Кэш устарел или отсутствует — фетчим новое
        fresh_data = await self._fetch_fresh_prices()
        
        # Сохраняем в кэш
        with open(self.cache_file, "w", encoding="utf-8") as f:
            json.dump(fresh_data, f, ensure_ascii=False, indent=2)
        
        return {"source": "fresh", **fresh_data}
