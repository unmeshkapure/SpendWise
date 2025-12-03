from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Dict
from ..ml.predictor import BudgetPredictor
from ..models.transaction import Transaction

class PredictionService:
    def __init__(self, db: Session, model_path: str = "app/ml/models/budget_predictor.pkl"):
        self.db = db
        self.predictor = BudgetPredictor(model_path)
        self.load_existing_model()
    
    def load_existing_model(self):
        self.predictor.load_model()
    
    def get_historical_transactions(self, user_id: int, months_back: int = 12) -> List[Dict]:
        from sqlalchemy import func
        
        start_date = datetime.now() - timedelta(days=months_back * 30)
        
        transactions = self.db.query(
            Transaction.amount,
            Transaction.date,
            Transaction.category
        ).filter(
            Transaction.user_id == user_id,
            Transaction.type == "expense",
            Transaction.date >= start_date,
            Transaction.is_active == True
        ).order_by(Transaction.date).all()
        
        return [
            {
                "amount": float(row.amount),
                "date": row.date,
                "category": row.category
            }
            for row in transactions
        ]
    
    def train_model_for_user(self, user_id: int) -> Dict[str, float]:
        transactions = self.get_historical_transactions(user_id)
        
        if len(transactions) < 3:
            return {
                "message": "Not enough data to train model",
                "training_samples": len(transactions)
            }
        
        return self.predictor.train_model(transactions)
    
    def predict_next_month_budget(self, user_id: int) -> Dict[str, float]:
        try:
            from sqlalchemy import func
            
            current_month = datetime.now().month
            current_year = datetime.now().year
            
            current_month_transactions = self.db.query(Transaction).filter(
                Transaction.user_id == user_id,
                Transaction.type == "expense",
                Transaction.date >= datetime(current_year, current_month, 1),
                Transaction.date < (datetime(current_year, current_month + 1, 1) if current_month < 12 else datetime(current_year + 1, 1, 1)),
                Transaction.is_active == True
            ).all()
            
            avg_amount = sum(t.amount for t in current_month_transactions) / len(current_month_transactions) if current_month_transactions else 2000.0
            category_diversity = len(set(t.category for t in current_month_transactions)) if current_month_transactions else 5
            transaction_count = len(current_month_transactions)
            
            next_month = current_month + 1 if current_month < 12 else 1
            next_year = current_year if current_month < 12 else current_year + 1
            
            predicted_budget = self.predictor.predict_budget(
                month=next_month,
                year=next_year,
                avg_amount=avg_amount,
                category_diversity=category_diversity,
                transaction_count=transaction_count
            )
            
            current_month_expense = self.db.query(func.sum(Transaction.amount)).filter(
                Transaction.user_id == user_id,
                Transaction.type == "expense",
                Transaction.date >= datetime(current_year, current_month, 1),
                Transaction.date < (datetime(current_year, current_month + 1, 1) if current_month < 12 else datetime(current_year + 1, 1, 1)),
                Transaction.is_active == True
            ).scalar() or 0.0
            
            return {
                "predicted_budget": predicted_budget,
                "current_month_spending": current_month_expense,
                "next_month": next_month,
                "next_year": next_year,
                "recommendation": "Increase" if predicted_budget > current_month_expense * 1.1 else "Maintain" if abs(predicted_budget - current_month_expense) < current_month_expense * 0.1 else "Reduce"
            }
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise e

    def get_spending_trends(self, user_id: int, months_back: int = 6) -> List[Dict]:
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
            
            total_expense = self.db.query(func.sum(Transaction.amount)).filter(
                Transaction.user_id == user_id,
                Transaction.type == "expense",
                Transaction.date >= start_date,
                Transaction.date < end_date,
                Transaction.is_active == True
            ).scalar() or 0.0
            
            total_income = self.db.query(func.sum(Transaction.amount)).filter(
                Transaction.user_id == user_id,
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
        
        return trends[::-1]