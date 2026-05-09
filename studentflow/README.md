# 🎓 StudentFlow - Умный трекер личных финансов для студента

**Приложение для управления личными финансами студента технического вуза с прогнозированием бюджета и автоподгрузкой цен.**

---

## 📁 Структура проекта

```
studentflow/
├── backend/
│   ├── main.py                 # FastAPI приложение
│   ├── requirements.txt        # Зависимости Python
│   ├── models/
│   │   └── database.py         # SQLite модель и инициализация БД
│   ├── routers/
│   │   ├── transactions.py     # CRUD для транзакций
│   │   └── finance.py          # Эндпоинты: баланс, прогноз, цены
│   ├── services/
│   │   ├── forecast.py         # Логика прогнозирования бюджета
│   │   └── p5_prices.py        # Сервис получения цен Пятёрочки
│   └── data/
│       ├── studentflow.db      # SQLite база данных
│       └── transport_prices.json  # Тарифы транспорта Москвы
├── data/
│   └── transport_prices.json   # Копия тарифов (для фронтенда)
└── frontend/                   # (будущий React/Vue проект)
```

---

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
cd backend
pip install -r requirements.txt
```

### 2. Запуск сервера

```bash
python main.py
# или
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Сервер запустится на `http://localhost:8000`

### 3. Проверка работы

- **API документация**: http://localhost:8000/docs
- **Health check**: http://localhost:8000/health
- **Баланс**: http://localhost:8000/api/balance/current
- **Прогноз**: http://localhost:8000/api/forecast?days=30

---

## 📡 API Endpoints

### Транзакции

| Метод | Endpoint | Описание |
|-------|----------|----------|
| `POST` | `/api/transactions/` | Добавить транзакцию |
| `GET` | `/api/transactions/?limit=50&offset=0` | Список транзакций |
| `DELETE` | `/api/transactions/{id}` | Удалить транзакцию |

**Пример добавления расхода:**
```bash
curl -X POST "http://localhost:8000/api/transactions/" \
  -H "Content-Type: application/json" \
  -d '{"date":"2026-05-09","type":"expense","category":"food","amount":280,"description":"Обед"}'
```

### Финансы и прогноз

| Метод | Endpoint | Описание |
|-------|----------|----------|
| `GET` | `/api/balance/current` | Текущий баланс |
| `GET` | `/api/forecast?days=30` | Прогноз на N дней |
| `GET` | `/api/prices/transport` | Тарифы транспорта |
| `GET` | `/api/prices/p5/basket` | Цены Пятёрочки (кэш) |
| `POST` | `/api/settings/exam-mode?enabled=true` | Режим сессии |

---

## 🧮 Логика прогнозирования

Класс `BudgetForecaster` в `backend/services/forecast.py`:

1. **Считает средние дневные траты** по истории транзакций
2. **Генерирует мягкую кривую** с коридором неопределённости (±15-40%)
3. **Учитывает фиксированные расходы** (подписки, интернет)
4. **Режим сессии**: увеличивает траты на 15% в последнюю треть периода
5. **Возвращает рекомендацию** на основе прогноза

**Пример ответа `/api/forecast?days=14`:**
```json
{
  "current_balance": 3155.0,
  "daily_avg_expense": 172.5,
  "exam_mode": false,
  "curve": [
    {"day": 0, "date": "2026-05-09", "expected": 3155.0, "min": 2681.75, "max": 3438.95, "risk_zone": "green"},
    {"day": 7, "date": "2026-05-16", "expected": 1950.5, "min": 1560.4, "max": 2184.56, "risk_zone": "yellow"}
  ],
  "recommendation": "⚠️ Бюджет напряжённый. Рекомендуем сократить необязательные расходы на 10-15%.",
  "external_prices": {
    "transport": {"troika_wallet": 42, "student_metro_monthly": 545},
    "p5_basket": {"total": 847, "source": "cache"}
  }
}
```

---

## 🗄 База данных (SQLite)

### Таблицы:

1. **transactions** — основные записи о доходах/расходах
2. **user_settings** — настройки пользователя (режим сессии, ID магазина)
3. **price_cache** — кэш внешних данных (цены, тарифы)

**Инициализация БД:**
```bash
python -c "from models.database import init_db; init_db()"
```

---

## 🚌 Транспорт Москвы

Файл `data/transport_prices.json` содержит актуальные тарифы:

- **Тройка**: кошелёк (42₽), 90 минут (65₽)
- **Единый**: 1 день, 3 дня, 30 дней, 90 дней
- **Студенческие льготы**: метро (545₽/мес), автобус (345₽/мес), комбинированный (890₽/мес)

**Проверка обновления:**
При запуске проверяется поле `next_check`. Если дата прошла → API вернёт `needs_update: true`.

---

## 🛒 Продукты Пятёрочки

Сервис `P5PriceService` (`backend/services/p5_prices.py`):

- Использует библиотеку `pyaterochka_api`
- Кэширует цены на 168 часов (7 дней)
- Считает сумму базовой корзины студента (6 товаров)

**Для активации:**
```bash
pip install pyaterochka_api
python -m camoufox fetch  # инициализация браузера
```

---

## 🎨 Требования к фронтенду (React/Vue)

### Цветовая схема (CSS variables):
```css
:root {
  --bg-primary: #0f172a;
  --bg-secondary: #1e293b;
  --text-primary: #f1f5f9;
  --accent-green: #86efac;
  --accent-yellow: #fde047;
  --accent-red: #fca5a5;
  --accent-blue: #93c5fd;
}
```

### Ключевые компоненты:
1. **SoftAreaChart** — мягкий график с градиентами (Recharts)
2. **TransactionInput** — ввод траты с категориями (свайп/кнопки)
3. **ExamModeToggle** — переключатель режима сессии
4. **ForecastSlider** — слайдер экономии с перестроением графика

---

## ✅ Чеклист MVP

### Этап 1: Бэкенд-ядро ✅
- [x] Инициализировать FastAPI проект
- [x] Создать SQLite БД
- [x] CRUD для транзакций
- [x] Сервис P5PriceService (заготовка)
- [x] Файл transport_prices.json
- [x] Класс BudgetForecaster

### Этап 2: API эндпоинты ✅
- [x] GET /api/balance/current
- [x] POST /api/transactions
- [x] GET /api/forecast?days=30
- [x] GET /api/prices/transport
- [x] POST /api/settings/exam-mode

### Этап 3: Фронтенд-прототип ⏳
- [ ] Настроить React + Vite + Tailwind
- [ ] Главный дашборд: баланс + график
- [ ] Ввод траты
- [ ] Recharts SoftAreaChart
- [ ] Переключатель режима сессии

### Этап 4: Интеграция и полировка ⏳
- [ ] Кэширование цен (фоновая задача)
- [ ] Обработка ошибок
- [ ] Экспорт в PNG (html2canvas)
- [ ] Мобильный адаптив

---

## 🧪 Тестирование

### Пример тестовых запросов:

```bash
# 1. Добавить доход
curl -X POST "http://localhost:8000/api/transactions/" \
  -H "Content-Type: application/json" \
  -d '{"date":"2026-05-09","type":"income","category":"stipend","amount":3500}'

# 2. Добавить расход
curl -X POST "http://localhost:8000/api/transactions/" \
  -H "Content-Type: application/json" \
  -d '{"date":"2026-05-09","type":"expense","category":"food","amount":280}'

# 3. Получить баланс
curl http://localhost:8000/api/balance/current

# 4. Получить прогноз
curl "http://localhost:8000/api/forecast?days=14"

# 5. Включить режим сессии
curl -X POST "http://localhost:8000/api/settings/exam-mode?enabled=true"
```

---

## 🔧 Расширение (бонусы)

1. **Telegram-бот**: быстрый ввод трат через чат
2. **Голосовой ввод**: «Запиши: потратил 65 рублей на метро»
3. **Сравнение с одногруппниками** (анонимно)
4. **Интеграция с календарём**: автодобавление подписок
5. **PWA-режим**: оффлайн-работа

---

## 📝 Лицензия

MIT License — используйте для учёбы и личных проектов.

---

**Разработано для студентов технических вузов Москвы 💙🎓**
