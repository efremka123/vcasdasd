"""
Database module for StudentFlow - handles SQLite connections and schema initialization.
"""
import sqlite3
from pathlib import Path
from typing import Optional


# Database configuration
DB_PATH = Path(__file__).parent.parent / "data" / "studentflow.db"

# Database schema definition
SCHEMA = """
-- transactions: Core transaction records
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

-- user_settings: User preferences and settings
CREATE TABLE IF NOT EXISTS user_settings (
    key TEXT PRIMARY KEY,
    value TEXT
);

-- price_cache: Cache for external price data
CREATE TABLE IF NOT EXISTS price_cache (
    source TEXT NOT NULL,
    cache_key TEXT NOT NULL,
    data TEXT NOT NULL,
    fetched_at DATETIME NOT NULL,
    expires_at DATETIME NOT NULL,
    PRIMARY KEY (source, cache_key)
);

-- Indexes for query optimization
CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date);
CREATE INDEX IF NOT EXISTS idx_transactions_category ON transactions(category);
CREATE INDEX IF NOT EXISTS idx_price_cache_expires ON price_cache(expires_at);
"""


class DatabaseManager:
    """Manages database connections and operations."""
    
    def __init__(self, db_path: Optional[Path] = None):
        """Initialize database manager with optional custom path."""
        self.db_path = db_path or DB_PATH
    
    def get_connection(self) -> sqlite3.Connection:
        """Get a database connection with row factory enabled."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def initialize(self) -> None:
        """Initialize database schema, creating tables if they don't exist."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = self.get_connection()
        try:
            conn.executescript(SCHEMA)
            conn.commit()
        finally:
            conn.close()
        print(f"✅ Database initialized: {self.db_path}")


# Module-level convenience functions
_db_manager: Optional[DatabaseManager] = None


def get_db_manager() -> DatabaseManager:
    """Get or create the global database manager instance."""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager


def get_db_connection() -> sqlite3.Connection:
    """Get a database connection (convenience function)."""
    return get_db_manager().get_connection()


def init_db() -> None:
    """Initialize the database (convenience function)."""
    get_db_manager().initialize()


if __name__ == "__main__":
    init_db()
