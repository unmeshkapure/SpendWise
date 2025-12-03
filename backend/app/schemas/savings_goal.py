from pydantic import BaseModel, field_validator
from datetime import date
from typing import Optional

class SavingsGoalBase(BaseModel):
    title: str
    target_amount: float
    target_date: date
    description: Optional[str] = None

class SavingsGoalCreate(SavingsGoalBase):
    @field_validator('target_amount')
    def validate_target_amount(cls, v):
        if v <= 0:
            raise ValueError('Target amount must be positive')
        return v
    
    @field_validator('target_date')
    def validate_target_date(cls, v):
        from datetime import date
        if v <= date.today():
            raise ValueError('Target date must be in the future')
        return v

class SavingsGoalUpdate(BaseModel):
    title: Optional[str] = None
    target_amount: Optional[float] = None
    target_date: Optional[date] = None
    description: Optional[str] = None

class SavingsGoalInDB(SavingsGoalBase):
    id: int
    user_id: int
    current_amount: float
    is_locked: bool
    is_completed: bool
    created_at: date
    unlocked_at: Optional[date] = None
    
    class Config:
        from_attributes = True

class SavingsGoalResponse(BaseModel):
    id: int
    title: str
    target_amount: float
    current_amount: float
    target_date: date
    is_locked: bool
    is_completed: bool
    progress_percentage: float
    days_remaining: int
    description: Optional[str]
    user_id: int
    
    class Config:
        from_attributes = True