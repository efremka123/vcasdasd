from pyaterochka_api import PyaterochkaAPI
import asyncio
import json
from datetime import datetime, timedelta
import os


class P5PriceService:
    def __init__(self, store_sap_code: str = "12345", cache_ttl_hours: int = 168):
        self.store_sap_code = store_sap_code  # ID конкретного магазина
        self.cache_ttl = timedelta(hours=cache_ttl_hours)
        self.cache_file = "data/p5_prices_cache.json"
        self.use_mock = os.environ.get("P5_MOCK_MODE", "true").lower() == "true"
    
    async def _fetch_fresh_prices(self) -> dict:
        """Получает актуальные цены из API Пятёрочки"""
        if self.use_mock:
            # Mock-данные для демонстрации (если нет места для camoufox)
            print("ℹ️ Используем mock-данные для Пятёрочки (P5_MOCK_MODE=true)")
            mock_products = [
                {"id": "1001", "name": "Молоко 3.2%, 1л", "price": 89.99, "unit": "шт"},
                {"id": "1045", "name": "Яйца С1, 10 шт", "price": 119.99, "unit": "уп"},
                {"id": "2034", "name": "Хлеб пшеничный", "price": 45.99, "unit": "шт"},
                {"id": "3012", "name": "Макароны, 450г", "price": 69.99, "unit": "уп"},
                {"id": "4056", "name": "Куриное филе, 1кг", "price": 299.99, "unit": "кг"},
                {"id": "5023", "name": "Овощи сезонные", "price": 129.99, "unit": "кг"},
            ]
            return {
                "store_code": self.store_sap_code,
                "fetched_at": datetime.now().isoformat(),
                "products": mock_products,
                "basket_total": sum(p["price"] for p in mock_products),
                "mock": True
            }
        
        try:
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
        except Exception as e:
            print(f"⚠️ Ошибка при получении цен из API: {e}")
            # Возвращаем mock-данные при ошибке
            return await self._get_mock_data()
    
    async def _get_mock_data(self) -> dict:
        """Fallback mock-данные"""
        mock_products = [
            {"id": "1001", "name": "Молоко 3.2%, 1л", "price": 89.99, "unit": "шт"},
            {"id": "1045", "name": "Яйца С1, 10 шт", "price": 119.99, "unit": "уп"},
            {"id": "2034", "name": "Хлеб пшеничный", "price": 45.99, "unit": "шт"},
            {"id": "3012", "name": "Макароны, 450г", "price": 69.99, "unit": "уп"},
            {"id": "4056", "name": "Куриное филе, 1кг", "price": 299.99, "unit": "кг"},
            {"id": "5023", "name": "Овощи сезонные", "price": 129.99, "unit": "кг"},
        ]
        return {
            "store_code": self.store_sap_code,
            "fetched_at": datetime.now().isoformat(),
            "products": mock_products,
            "basket_total": sum(p["price"] for p in mock_products),
            "mock": True,
            "fallback": True
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
