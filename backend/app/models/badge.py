from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..config.database import Base

class Badge(Base):
    """Badge model for gamification system"""
    
    __tablename__ = "badges"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # e.g., "Saver Elite", "Budget Master"
    description = Column(String)
    icon = Column(String)  # e.g., "🏆", "🏅", "💰"
    criteria = Column(String, nullable=False)  # e.g., "saved_5000", "budget_streak_30"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    user_badges = relationship("UserBadge", back_populates="badge")

class UserBadge(Base):
    """User-Badge relationship for tracking earned badges"""
    
    __tablename__ = "user_badges"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    badge_id = Column(Integer, ForeignKey("badges.id"), nullable=False)
    earned_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="user_badges")
    badge = relationship("Badge", back_populates="user_badges")

# Add relationship to User model
def add_user_relationship():
    from .user import User
    User.user_badges = relationship("UserBadge", back_populates="user")

# Call the function to set up relationships
add_user_relationship()