from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional

class TransactionBase(BaseModel):
    amount: float
    category: str
    type: str
    description: Optional[str] = None
    date: Optional[datetime] = None

class TransactionCreate(TransactionBase):
    @field_validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be positive')
        return v
    
    @field_validator('type')
    def validate_type(cls, v):
        if v.lower() not in ['income', 'expense']:
            raise ValueError('Type must be either "income" or "expense"')
        return v.lower()

    @field_validator('date', mode='before')
    def parse_date(cls, v):
        if isinstance(v, str):
            try:
                # Handle YYYY-MM-DD format
                return datetime.strptime(v, '%Y-%m-%d')
            except ValueError:
                pass
        return v

class TransactionUpdate(BaseModel):
    amount: Optional[float] = None
    category: Optional[str] = None
    description: Optional[str] = None

class TransactionInDB(TransactionBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class TransactionResponse(BaseModel):
    id: int
    amount: float
    category: str
    type: str
    description: Optional[str]
    date: datetime
    user_id: int
    
    class Config:
        from_attributes = True