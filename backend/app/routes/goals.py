from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

from ..config.database import get_db
from ..models.saving_goal import SavingsGoal
from ..schemas.savings_goal import SavingsGoalCreate, SavingsGoalUpdate, SavingsGoalResponse
from ..routes.auth import get_current_user
from ..models.user import User

router = APIRouter()

@router.post("/", response_model=SavingsGoalResponse)
def create_savings_goal(
    goal_data: SavingsGoalCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new savings goal"""
    goal = SavingsGoal(
        user_id=current_user.id,
        title=goal_data.title,
        target_amount=goal_data.target_amount,
        target_date=goal_data.target_date,
        description=goal_data.description
    )
    
    db.add(goal)
    db.commit()
    db.refresh(goal)
    
    # Calculate derived properties
    progress_percentage = min(100, (goal.current_amount / goal.target_amount) * 100) if goal.target_amount > 0 else 0
    days_remaining = (goal.target_date - datetime.now()).days if goal.target_date > datetime.now() else 0
    
    return SavingsGoalResponse(
        id=goal.id,
        title=goal.title,
        target_amount=goal.target_amount,
        current_amount=goal.current_amount,
        target_date=goal.target_date,
        is_locked=goal.is_locked,
        is_completed=goal.is_completed,
        progress_percentage=progress_percentage,
        days_remaining=days_remaining,
        description=goal.description,
        user_id=goal.user_id
    )

@router.get("/", response_model=List[SavingsGoalResponse])
def get_savings_goals(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all savings goals for current user"""
    goals = db.query(SavingsGoal).filter(
        SavingsGoal.user_id == current_user.id
    ).all()
    
    result = []
    for goal in goals:
        progress_percentage = min(100, (goal.current_amount / goal.target_amount) * 100) if goal.target_amount > 0 else 0
        days_remaining = (goal.target_date - datetime.now()).days if goal.target_date > datetime.now() else 0
        
        result.append(SavingsGoalResponse(
            id=goal.id,
            title=goal.title,
            target_amount=goal.target_amount,
            current_amount=goal.current_amount,
            target_date=goal.target_date,
            is_locked=goal.is_locked,
            is_completed=goal.is_completed,
            progress_percentage=progress_percentage,
            days_remaining=days_remaining,
            description=goal.description,
            user_id=goal.user_id
        ))
    
    return result

@router.get("/{goal_id}", response_model=SavingsGoalResponse)
def get_savings_goal(
    goal_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific savings goal"""
    goal = db.query(SavingsGoal).filter(
        SavingsGoal.id == goal_id,
        SavingsGoal.user_id == current_user.id
    ).first()
    
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Savings goal not found"
        )
    
    progress_percentage = min(100, (goal.current_amount / goal.target_amount) * 100) if goal.target_amount > 0 else 0
    days_remaining = (goal.target_date - datetime.now()).days if goal.target_date > datetime.now() else 0
    
    return SavingsGoalResponse(
        id=goal.id,
        title=goal.title,
        target_amount=goal.target_amount,
        current_amount=goal.current_amount,
        target_date=goal.target_date,
        is_locked=goal.is_locked,
        is_completed=goal.is_completed,
        progress_percentage=progress_percentage,
        days_remaining=days_remaining,
        description=goal.description,
        user_id=goal.user_id
    )

@router.put("/{goal_id}", response_model=SavingsGoalResponse)
def update_savings_goal(
    goal_id: int,
    goal_data: SavingsGoalUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update savings goal"""
    goal = db.query(SavingsGoal).filter(
        SavingsGoal.id == goal_id,
        SavingsGoal.user_id == current_user.id
    ).first()
    
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Savings goal not found"
        )
    
    if goal.is_locked and goal.is_completed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update a completed and locked goal"
        )
    
    # Update fields that are provided
    for field, value in goal_data.dict(exclude_unset=True).items():
        setattr(goal, field, value)
    
    db.commit()
    db.refresh(goal)
    
    progress_percentage = min(100, (goal.current_amount / goal.target_amount) * 100) if goal.target_amount > 0 else 0
    days_remaining = (goal.target_date - datetime.now()).days if goal.target_date > datetime.now() else 0
    
    return SavingsGoalResponse(
        id=goal.id,
        title=goal.title,
        target_amount=goal.target_amount,
        current_amount=goal.current_amount,
        target_date=goal.target_date,
        is_locked=goal.is_locked,
        is_completed=goal.is_completed,
        progress_percentage=progress_percentage,
        days_remaining=days_remaining,
        description=goal.description,
        user_id=goal.user_id
    )

@router.delete("/{goal_id}")
def delete_savings_goal(
    goal_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete savings goal"""
    goal = db.query(SavingsGoal).filter(
        SavingsGoal.id == goal_id,
        SavingsGoal.user_id == current_user.id
    ).first()
    
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Savings goal not found"
        )
    
    if goal.is_locked:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete a locked goal"
        )
    
    db.delete(goal)
    db.commit()
    
    return {"message": "Savings goal deleted successfully"}

@router.post("/{goal_id}/add-amount")
def add_amount_to_goal(
    goal_id: int,
    amount: float,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add amount to savings goal"""
    goal = db.query(SavingsGoal).filter(
        SavingsGoal.id == goal_id,
        SavingsGoal.user_id == current_user.id
    ).first()
    
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Savings goal not found"
        )

    if amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Amount must be positive"
        )

    goal.current_amount += amount
    
    if goal.current_amount >= goal.target_amount:
        goal.is_completed = True
        goal.is_locked = True
    
    db.commit()
    db.refresh(goal)
    
    progress_percentage = min(100, (goal.current_amount / goal.target_amount) * 100) if goal.target_amount > 0 else 0
    days_remaining = (goal.target_date - datetime.now()).days if goal.target_date > datetime.now() else 0
    
    return SavingsGoalResponse(
        id=goal.id,
        title=goal.title,
        target_amount=goal.target_amount,
        current_amount=goal.current_amount,
        target_date=goal.target_date,
        is_locked=goal.is_locked,
        is_completed=goal.is_completed,
        progress_percentage=progress_percentage,
        days_remaining=days_remaining,
        description=goal.description,
        user_id=goal.user_id
    )