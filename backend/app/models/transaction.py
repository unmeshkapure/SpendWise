from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..config.database import Base

class Transaction(Base):
    """Transaction model for tracking income and expenses"""
    
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    category = Column(String, nullable=False)  # e.g., "Food", "Entertainment", "Salary"
    type = Column(String, nullable=False)      # "income" or "expense"
    description = Column(String)
    date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Relationship
    user = relationship("User", back_populates="transactions")
    
    def __repr__(self):
        return f"<Transaction(id={self.id}, user_id={self.user_id}, amount={self.amount}, type='{self.type}')>"
    
    @property
    def is_expense(self):
        return self.type.lower() == "expense"
    
    @property
    def is_income(self):
        return self.type.lower() == "income"

# Add relationship to User model - this should be at the end of the file
def add_user_relationship():
    from .user import User
    User.transactions = relationship("Transaction", back_populates="user")

# Call the function to set up relationships
add_user_relationship()