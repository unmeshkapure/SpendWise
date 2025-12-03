from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Dict

from ..config.database import get_db
from ..models.badge import Badge, UserBadge
from ..routes.auth import get_current_user
from ..models.user import User
from ..models.transaction import Transaction
from ..models.saving_goal import SavingsGoal

router = APIRouter()

@router.get("/")
def get_user_badges(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all badges earned by the user"""
    from sqlalchemy import func
    
    # Get user's earned badges
    user_badges = db.query(UserBadge).filter(
        UserBadge.user_id == current_user.id
    ).join(Badge).all()
    
    # Calculate potential badges based on user's activity
    potential_badges = []
    
    # Get user's transaction summary
    total_saved = db.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == current_user.id,
        Transaction.type == "income"
    ).scalar() or 0.0
    
    total_spent = db.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == current_user.id,
        Transaction.type == "expense"
    ).scalar() or 0.0
    
    net_savings = total_saved - total_spent
    
    # Check for "Saver Elite" badge (saved 5000+)
    if net_savings >= 5000:
        saver_elite_badge = db.query(Badge).filter(
            Badge.criteria == "saved_5000"
        ).first()
        if saver_elite_badge:
            user_has_badge = db.query(UserBadge).filter(
                UserBadge.user_id == current_user.id,
                UserBadge.badge_id == saver_elite_badge.id
            ).first()
            if not user_has_badge:
                potential_badges.append({
                    "id": saver_elite_badge.id,
                    "name": saver_elite_badge.name,
                    "description": saver_elite_badge.description,
                    "icon": saver_elite_badge.icon,
                    "criteria": saver_elite_badge.criteria,
                    "earned": False
                })
    
    # Check for "Budget Master" badge (completed 3+ goals)
    completed_goals = db.query(SavingsGoal).filter(
        SavingsGoal.user_id == current_user.id,
        SavingsGoal.is_completed == True
    ).count()
    
    if completed_goals >= 3:
        budget_master_badge = db.query(Badge).filter(
            Badge.criteria == "completed_3_goals"
        ).first()
        if budget_master_badge:
            user_has_badge = db.query(UserBadge).filter(
                UserBadge.user_id == current_user.id,
                UserBadge.badge_id == budget_master_badge.id
            ).first()
            if not user_has_badge:
                potential_badges.append({
                    "id": budget_master_badge.id,
                    "name": budget_master_badge.name,
                    "description": budget_master_badge.description,
                    "icon": budget_master_badge.icon,
                    "criteria": budget_master_badge.criteria,
                    "earned": False
                })
    
    # Get all badges with earned status
    earned_badges = [
        {
            "id": ub.badge.id,
            "name": ub.badge.name,
            "description": ub.badge.description,
            "icon": ub.badge.icon,
            "criteria": ub.badge.criteria,
            "earned_at": ub.earned_at.isoformat(),
            "earned": True
        }
        for ub in user_badges
    ]
    
    return {
        "earned_badges": earned_badges,
        "potential_badges": potential_badges,
        "total_earned": len(earned_badges)
    }

@router.get("/available")
def get_available_badges(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all available badges in the system"""
    badges = db.query(Badge).all()
    
    return [
        {
            "id": badge.id,
            "name": badge.name,
            "description": badge.description,
            "icon": badge.icon,
            "criteria": badge.criteria
        }
        for badge in badges
    ]

@router.post("/award")
def award_badge(
    badge_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Award a badge to the user (for testing purposes)"""
    # Check if badge exists
    badge = db.query(Badge).filter(Badge.id == badge_id).first()
    if not badge:
        raise HTTPException(status_code=404, detail="Badge not found")
    
    # Check if user already has this badge
    existing_user_badge = db.query(UserBadge).filter(
        UserBadge.user_id == current_user.id,
        UserBadge.badge_id == badge_id
    ).first()
    
    if existing_user_badge:
        raise HTTPException(status_code=400, detail="User already has this badge")
    
    # Award badge
    user_badge = UserBadge(
        user_id=current_user.id,
        badge_id=badge_id
    )
    
    db.add(user_badge)
    db.commit()
    
    return {
        "message": "Badge awarded successfully",
        "badge": {
            "id": badge.id,
            "name": badge.name,
            "description": badge.description,
            "icon": badge.icon
        }
    }

def check_and_award_badges(user_id: int, db: Session):
    """Check user's progress and award badges automatically"""
    from sqlalchemy import func
    
    # Get user's transaction summary
    total_saved = db.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == user_id,
        Transaction.type == "income"
    ).scalar() or 0.0
    
    total_spent = db.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == user_id,
        Transaction.type == "expense"
    ).scalar() or 0.0
    
    net_savings = total_saved - total_spent
    
    # Check for "Saver Elite" badge (saved 5000+)
    if net_savings >= 5000:
        saver_elite_badge = db.query(Badge).filter(
            Badge.criteria == "saved_5000"
        ).first()
        if saver_elite_badge:
            user_has_badge = db.query(UserBadge).filter(
                UserBadge.user_id == user_id,
                UserBadge.badge_id == saver_elite_badge.id
            ).first()
            if not user_has_badge:
                user_badge = UserBadge(
                    user_id=user_id,
                    badge_id=saver_elite_badge.id
                )
                db.add(user_badge)
    
    # Check for "Budget Master" badge (completed 3+ goals)
    completed_goals = db.query(SavingsGoal).filter(
        SavingsGoal.user_id == user_id,
        SavingsGoal.is_completed == True
    ).count()
    
    if completed_goals >= 3:
        budget_master_badge = db.query(Badge).filter(
            Badge.criteria == "completed_3_goals"
        ).first()
        if budget_master_badge:
            user_has_badge = db.query(UserBadge).filter(
                UserBadge.user_id == user_id,
                UserBadge.badge_id == budget_master_badge.id
            ).first()
            if not user_has_badge:
                user_badge = UserBadge(
                    user_id=user_id,
                    badge_id=budget_master_badge.id
                )
                db.add(user_badge)
    
    db.commit()