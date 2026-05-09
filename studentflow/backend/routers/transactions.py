from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import json

from models.database import get_db_connection


router = APIRouter(prefix="/api/transactions", tags=["transactions"])


class TransactionCreate(BaseModel):
    date: str
    type: str  # 'income' or 'expense'
    category: str
    amount: float
    description: Optional[str] = None
    tags: Optional[List[str]] = None


class TransactionResponse(BaseModel):
    id: int
    date: str
    type: str
    category: str
    amount: float
    description: Optional[str]
    tags: Optional[List[str]]
    created_at: str


@router.post("/", response_model=TransactionResponse)
def create_transaction(transaction: TransactionCreate):
    """Добавить новую транзакцию (доход или расход)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    tags_json = json.dumps(transaction.tags) if transaction.tags else None
    
    cursor.execute(
        """INSERT INTO transactions (date, type, category, amount, description, tags)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (transaction.date, transaction.type, transaction.category,
         transaction.amount, transaction.description, tags_json)
    )
    
    conn.commit()
    transaction_id = cursor.lastrowid
    
    cursor.execute("SELECT * FROM transactions WHERE id = ?", (transaction_id,))
    row = cursor.fetchone()
    conn.close()
    
    return {
        "id": row["id"],
        "date": row["date"],
        "type": row["type"],
        "category": row["category"],
        "amount": row["amount"],
        "description": row["description"],
        "tags": json.loads(row["tags"]) if row["tags"] else None,
        "created_at": row["created_at"]
    }


@router.get("/", response_model=List[TransactionResponse])
def get_transactions(limit: int = 50, offset: int = 0):
    """Получить список транзакций с пагинацией"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT * FROM transactions ORDER BY date DESC LIMIT ? OFFSET ?",
        (limit, offset)
    )
    
    rows = cursor.fetchall()
    conn.close()
    
    return [
        {
            "id": row["id"],
            "date": row["date"],
            "type": row["type"],
            "category": row["category"],
            "amount": row["amount"],
            "description": row["description"],
            "tags": json.loads(row["tags"]) if row["tags"] else None,
            "created_at": row["created_at"]
        }
        for row in rows
    ]


@router.delete("/{transaction_id}")
def delete_transaction(transaction_id: int):
    """Удалить транзакцию"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
    
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Транзакция не найдена")
    
    conn.commit()
    conn.close()
    
    return {"message": "Транзакция удалена"}
