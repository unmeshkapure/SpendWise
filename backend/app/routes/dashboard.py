from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Dict, Any

from ..config.database import get_db
from ..models.transaction import Transaction
from ..routes.auth import get_current_user
from ..models.user import User

router = APIRouter()

@router.get("/summary")
def get_dashboard_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive dashboard summary"""
    from sqlalchemy import func
    
    # Get current month
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    # Calculate current month totals
    current_month_start = datetime(current_year, current_month, 1)
    if current_month == 12:
        current_month_end = datetime(current_year + 1, 1, 1)
    else:
        current_month_end = datetime(current_year, current_month + 1, 1)
    
    income_query = db.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == current_user.id,
        Transaction.type == "income",
        Transaction.date >= current_month_start,
        Transaction.date < current_month_end,
        Transaction.is_active == True
    ).scalar()
    
    expense_query = db.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == current_user.id,
        Transaction.type == "expense",
        Transaction.date >= current_month_start,
        Transaction.date < current_month_end,
        Transaction.is_active == True
    ).scalar()
    
    # Get recent transactions
    recent_transactions = db.query(Transaction).filter(
        Transaction.user_id == current_user.id,
        Transaction.is_active == True
    ).order_by(Transaction.date.desc()).limit(10).all()
    
    # Get category breakdown
    category_breakdown = db.query(
        Transaction.category,
        func.sum(Transaction.amount).label('total')
    ).filter(
        Transaction.user_id == current_user.id,
        Transaction.type == "expense",
        Transaction.date >= current_month_start,
        Transaction.date < current_month_end,
        Transaction.is_active == True
    ).group_by(Transaction.category).all()
    
    return {
        "summary": {
            "current_month_income": income_query or 0.0,
            "current_month_expense": expense_query or 0.0,
            "current_month_net": (income_query or 0.0) - (expense_query or 0.0)
        },
        "recent_transactions": [
            {
                "id": t.id,
                "amount": t.amount,
                "category": t.category,
                "type": t.type,
                "date": t.date.isoformat(),
                "description": t.description
            }
            for t in recent_transactions
        ],
        "category_breakdown": [
            {
                "category": row.category,
                "total": float(row.total)
            }
            for row in category_breakdown
        ]
    }

@router.get("/trends")
def get_spending_trends(
    months_back: int = 6,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get spending trends over the past few months"""
    from sqlalchemy import func
    
    trends = []
    today = datetime.now()
    
    for i in range(months_back):
        month = today.month - i
        year = today.year
        if month <= 0:
            month += 12
            year -= 1
        
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        
        total_expense = db.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == current_user.id,
            Transaction.type == "expense",
            Transaction.date >= start_date,
            Transaction.date < end_date,
            Transaction.is_active == True
        ).scalar() or 0.0
        
        total_income = db.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == current_user.id,
            Transaction.type == "income",
            Transaction.date >= start_date,
            Transaction.date < end_date,
            Transaction.is_active == True
        ).scalar() or 0.0
        
        trends.append({
            "month": month,
            "year": year,
            "total_expense": total_expense,
            "total_income": total_income,
            "net_savings": total_income - total_expense,
            "month_name": start_date.strftime("%B %Y")
        })
    
    return trends[::-1]  # Reverse to show oldest first

@router.get("/category-analysis")
def get_category_analysis(
    start_date: str = None,
    end_date: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed category analysis"""
    from sqlalchemy import func
    
    # Parse dates
    if start_date:
        start_date = datetime.fromisoformat(start_date)
    else:
        start_date = datetime.now() - timedelta(days=30)
    
    if end_date:
        end_date = datetime.fromisoformat(end_date)
    else:
        end_date = datetime.now()
    
    # Get category breakdown
    category_data = db.query(
        Transaction.category,
        func.sum(Transaction.amount).label('total_amount'),
        func.count(Transaction.id).label('transaction_count'),
        func.avg(Transaction.amount).label('avg_amount')
    ).filter(
        Transaction.user_id == current_user.id,
        Transaction.type == "expense",
        Transaction.date >= start_date,
        Transaction.date <= end_date,
        Transaction.is_active == True
    ).group_by(Transaction.category).order_by(func.sum(Transaction.amount).desc()).all()
    
    return [
        {
            "category": row.category,
            "total_amount": float(row.total_amount),
            "transaction_count": row.transaction_count,
            "avg_amount": float(row.avg_amount) if row.avg_amount else 0.0
        }
        for row in category_data
    ]