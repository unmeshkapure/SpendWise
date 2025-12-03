from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..config.database import Base

class SavingsGoal(Base):
    """Savings goal model with timed-lock functionality"""
    
    __tablename__ = "savings_goals"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    target_amount = Column(Float, nullable=False)
    current_amount = Column(Float, default=0.0)
    target_date = Column(Date, nullable=False)
    is_locked = Column(Boolean, default=True)  # Cannot withdraw until unlocked
    is_completed = Column(Boolean, default=False)
    description = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    unlocked_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationship
    user = relationship("User", back_populates="savings_goals")
    
    def __repr__(self):
        return f"<SavingsGoal(id={self.id}, user_id={self.user_id}, title='{self.title}', target_amount={self.target_amount})>"
    
    @property
    def progress_percentage(self):
        if self.target_amount == 0:
            return 0
        return min(100, (self.current_amount / self.target_amount) * 100)
    
    @property
    def days_remaining(self):
        from datetime import date
        if self.is_completed or self.target_date < date.today():
            return 0
        return (self.target_date - date.today()).days

# Add relationship to User model
def add_user_relationship():
    from .user import User
    User.savings_goals = relationship("SavingsGoal", back_populates="user")

# Call the function to set up relationships
add_user_relationship()