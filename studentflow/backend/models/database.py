import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).parent.parent / "data" / "studentflow.db"

INIT_SQL = """
-- transactions: основные записи
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    type TEXT CHECK(type IN ('income', 'expense')),
    category TEXT NOT NULL,
    amount REAL NOT NULL,
    description TEXT,
    tags TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- user_settings: настройки пользователя
CREATE TABLE IF NOT EXISTS user_settings (
    key TEXT PRIMARY KEY,
    value TEXT
);

-- price_cache: кэш внешних данных
CREATE TABLE IF NOT EXISTS price_cache (
    source TEXT NOT NULL,
    cache_key TEXT NOT NULL,
    data TEXT NOT NULL,
    fetched_at DATETIME NOT NULL,
    expires_at DATETIME NOT NULL,
    PRIMARY KEY (source, cache_key)
);

-- Индексы для ускорения выборок
CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date);
CREATE INDEX IF NOT EXISTS idx_transactions_category ON transactions(category);
CREATE INDEX IF NOT EXISTS idx_price_cache_expires ON price_cache(expires_at);
"""


def get_db_connection():
    """Возвращает соединение с БД"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Инициализирует БД, создаёт таблицы"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = get_db_connection()
    conn.executescript(INIT_SQL)
    conn.commit()
    conn.close()
    print(f"✅ База данных инициализирована: {DB_PATH}")


if __name__ == "__main__":
    init_db()
