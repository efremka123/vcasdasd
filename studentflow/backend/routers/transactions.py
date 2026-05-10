"""
Transaction management endpoints for StudentFlow API.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
import json

from backend.models.database import get_db_connection


router = APIRouter(prefix="/api/transactions", tags=["transactions"])


# Pydantic models for request/response validation
class TransactionCreate(BaseModel):
    """Schema for creating a new transaction."""
    date: str = Field(..., description="Transaction date in YYYY-MM-DD format")
    type: str = Field(..., description="Transaction type: 'income' or 'expense'")
    category: str = Field(..., description="Transaction category")
    amount: float = Field(..., gt=0, description="Transaction amount")
    description: Optional[str] = Field(None, description="Optional description")
    tags: Optional[List[str]] = Field(None, description="Optional list of tags")


class TransactionResponse(BaseModel):
    """Schema for transaction response."""
    id: int
    date: str
    type: str
    category: str
    amount: float
    description: Optional[str]
    tags: Optional[List[str]]
    created_at: str


def _row_to_dict(row) -> dict:
    """Convert database row to transaction dictionary."""
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


@router.post("/", response_model=TransactionResponse)
def create_transaction(transaction: TransactionCreate):
    """Create a new transaction (income or expense)."""
    conn = get_db_connection()
    try:
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
        
        return _row_to_dict(row)
    finally:
        conn.close()


@router.get("/", response_model=List[TransactionResponse])
def get_transactions(limit: int = 50, offset: int = 0):
    """Get list of transactions with pagination."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM transactions ORDER BY date DESC LIMIT ? OFFSET ?",
            (limit, offset)
        )
        
        rows = cursor.fetchall()
        return [_row_to_dict(row) for row in rows]
    finally:
        conn.close()


@router.delete("/{transaction_id}")
def delete_transaction(transaction_id: int):
    """Delete a transaction by ID."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        conn.commit()
        return {"message": "Transaction deleted successfully"}
    finally:
        conn.close()
