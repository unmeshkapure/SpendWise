from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Dict, Any

from ..config.database import get_db
from ..routes.auth import get_current_user
from ..models.user import User
from ..models.transaction import Transaction
from ..services.prediction_service import PredictionService

router = APIRouter()

@router.get("/budget")
def get_budget_prediction(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get budget prediction for next month"""
    service = PredictionService(db)
    
    # Auto-train if not trained
    if not service.predictor.is_trained:
        try:
            service.train_model_for_user(current_user.id)
        except Exception as e:
            print(f"Auto-training failed (expected for new users): {e}")
            
    prediction = service.predict_next_month_budget(current_user.id)
    return prediction

@router.post("/train-model")
def train_budget_model(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Train budget prediction model for user"""
    service = PredictionService(db)
    result = service.train_model_for_user(current_user.id)
    return result

@router.get("/trends")
def get_spending_trends(
    months_back: int = 6,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get spending trends for analysis"""
    service = PredictionService(db)
    trends = service.get_spending_trends(current_user.id, months_back)
    return trends

@router.get("/forecast")
def get_forecast(
    months_ahead: int = 3,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get forecast for next few months"""
    service = PredictionService(db)
    
    # Auto-train if not trained
    if not service.predictor.is_trained:
        try:
            service.train_model_for_user(current_user.id)
        except Exception as e:
            print(f"Auto-training failed (expected for new users): {e}")
    
    print("DEBUG: Starting forecast")
    forecasts = []
    for i in range(1, months_ahead + 1):
        # Calculate target month and year
        current_date = datetime.now()
        target_month = current_date.month + i
        target_year = current_date.year
        
        while target_month > 12:
            target_month -= 12
            target_year += 1
        
        print(f"DEBUG: Processing month {i}, target: {target_month}/{target_year}")
        
        # Get current month stats for features
        try:
            current_month_transactions = db.query(Transaction).filter(
                Transaction.user_id == current_user.id,
                Transaction.type == "expense",
                Transaction.date >= datetime(current_date.year, current_date.month, 1),
                Transaction.date < (datetime(current_date.year, current_date.month + 1, 1) if current_date.month < 12 else datetime(current_date.year + 1, 1, 1)),
                Transaction.is_active == True
            ).all()
            print(f"DEBUG: Found {len(current_month_transactions)} transactions")
        except Exception as e:
            print(f"DEBUG: Error querying transactions: {e}")
            raise e
        
        avg_amount = sum(t.amount for t in current_month_transactions) / len(current_month_transactions) if current_month_transactions else 2000.0
        category_diversity = len(set(t.category for t in current_month_transactions)) if current_month_transactions else 5
        transaction_count = len(current_month_transactions)
        
        print(f"DEBUG: Stats - Avg: {avg_amount}, Div: {category_diversity}, Count: {transaction_count}")
        
        try:
            predicted_budget = service.predictor.predict_budget(
                month=target_month,
                year=target_year,
                avg_amount=avg_amount,
                category_diversity=category_diversity,
                transaction_count=transaction_count
            )
            print(f"DEBUG: Predicted budget: {predicted_budget}")
        except Exception as e:
            print(f"DEBUG: Error predicting budget: {e}")
            raise e
        
        forecasts.append({
            "month": target_month,
            "year": target_year,
            "predicted_budget": predicted_budget,
            "month_name": datetime(target_year, target_month, 1).strftime("%B %Y")
        })
    
    return forecasts