from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from ..models.transaction import Transaction
from ..schemas.transaction import TransactionCreate, TransactionUpdate
from ..utils.validators import validate_transaction_data

class TransactionService:
    """Business logic for transaction operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_transaction(self, user_id: int, transaction_data: TransactionCreate) -> Transaction:
        """Create a new transaction"""
        # Validate transaction data
        validate_transaction_data(transaction_data.model_dump())
        
        # Create transaction object
        transaction = Transaction(
            user_id=user_id,
            amount=transaction_data.amount,
            category=transaction_data.category,
            type=transaction_data.type,
            description=transaction_data.description,
            date=transaction_data.date or datetime.utcnow()
        )
        
        # Add to database
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        
        return transaction
    
    def get_transactions_by_user(self, user_id: int, limit: int = 100, offset: int = 0) -> List[Transaction]:
        """Get all transactions for a user"""
        return self.db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.is_active == True
        ).order_by(Transaction.date.desc()).offset(offset).limit(limit).all()
    
    def get_transactions_by_date_range(self, user_id: int, start_date: datetime, end_date: datetime) -> List[Transaction]:
        """Get transactions within a date range"""
        return self.db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.date >= start_date,
            Transaction.date <= end_date,
            Transaction.is_active == True
        ).order_by(Transaction.date.desc()).all()
    
    def get_monthly_summary(self, user_id: int, month: int, year: int) -> dict:
        """Get monthly income and expense summary"""
        from sqlalchemy import func
        
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        
        income_query = self.db.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user_id,
            Transaction.type == "income",
            Transaction.date >= start_date,
            Transaction.date < end_date,
            Transaction.is_active == True
        ).scalar()
        
        expense_query = self.db.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user_id,
            Transaction.type == "expense",
            Transaction.date >= start_date,
            Transaction.date < end_date,
            Transaction.is_active == True
        ).scalar()
        
        return {
            "month": month,
            "year": year,
            "income": income_query or 0.0,
            "expense": expense_query or 0.0,
            "net": (income_query or 0.0) - (expense_query or 0.0),
            "start_date": start_date,
            "end_date": end_date
        }
    
    def get_category_summary(self, user_id: int, start_date: datetime, end_date: datetime) -> List[dict]:
        """Get expense summary by category"""
        from sqlalchemy import func
        
        results = self.db.query(
            Transaction.category,
            func.sum(Transaction.amount).label('total_amount'),
            func.count(Transaction.id).label('transaction_count')
        ).filter(
            Transaction.user_id == user_id,
            Transaction.type == "expense",
            Transaction.date >= start_date,
            Transaction.date <= end_date,
            Transaction.is_active == True
        ).group_by(Transaction.category).all()
        
        return [
            {
                "category": row.category,
                "total_amount": row.total_amount,
                "transaction_count": row.transaction_count
            }
            for row in results
        ]
    
    def update_transaction(self, transaction_id: int, update_data: TransactionUpdate) -> Optional[Transaction]:
        """Update an existing transaction"""
        transaction = self.db.query(Transaction).filter(
            Transaction.id == transaction_id
        ).first()
        
        if not transaction:
            return None
        
        # Update fields that are provided
        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(transaction, field, value)
        
        self.db.commit()
        self.db.refresh(transaction)
        return transaction
    
    def delete_transaction(self, transaction_id: int) -> bool:
        """Soft delete a transaction"""
        transaction = self.db.query(Transaction).filter(
            Transaction.id == transaction_id
        ).first()
        
        if not transaction:
            return False
        
        transaction.is_active = False
        self.db.commit()
        return True