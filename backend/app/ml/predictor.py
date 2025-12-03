import pandas as pd
import numpy as np
import sklearn
from sklearn.linear_model import ElasticNet
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import os
from datetime import datetime
from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)

class BudgetPredictor:
    """ML model for predicting monthly budget based on historical spending"""
    
    def __init__(self, model_path: str = "ml/models/budget_predictor.pkl"):
        self.model_path = model_path
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        
    def prepare_features(self, transactions: List[Dict]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare features for training/prediction
        Features: month, year, total_expense, category_diversity, average_transaction_amount
        """
        if not transactions:
            raise ValueError("No transactions provided")
        
        df = pd.DataFrame(transactions)
        
        # Convert date to datetime if it's not already
        df['date'] = pd.to_datetime(df['date'])
        
        # Extract features
        features = []
        targets = []
        
        # Group by month and year
        monthly_data = df.groupby([df['date'].dt.year, df['date'].dt.month]).agg({
            'amount': ['sum', 'mean', 'count'],
            'category': 'nunique'  # Number of unique categories
        }).round(2)
        
        # Flatten column names
        monthly_data.columns = ['total_expense', 'avg_amount', 'transaction_count', 'category_diversity']
        monthly_data = monthly_data.reset_index()
        monthly_data.columns = ['year', 'month', 'total_expense', 'avg_amount', 'transaction_count', 'category_diversity']
        
        # Create feature matrix
        for _, row in monthly_data.iterrows():
            features.append([
                row['month'],
                row['year'],
                row['avg_amount'],
                row['category_diversity'],
                row['transaction_count']
            ])
            targets.append(row['total_expense'])
        
        return np.array(features), np.array(targets)
    
    def train_model(self, transactions: List[Dict]) -> Dict[str, float]:
        """Train the budget prediction model"""
        try:
            X, y = self.prepare_features(transactions)
            
            if len(X) < 3:
                raise ValueError("Need at least 3 months of data to train")
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Create pipeline with model and scaler
            self.model = Pipeline([
                ('scaler', StandardScaler()),
                ('regressor', ElasticNet(alpha=0.1, l1_ratio=0.7, random_state=42))
            ])
            
            # Train model
            self.model.fit(X_train, y_train)
            
            # Evaluate model
            y_pred = self.model.predict(X_test)
            mae = mean_absolute_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            self.is_trained = True
            
            # Save model
            self.save_model()
            
            logger.info(f"Model trained successfully. MAE: {mae:.2f}, R²: {r2:.2f}")
            
            return {
                "mae": mae,
                "r2_score": r2,
                "training_samples": len(X_train),
                "test_samples": len(X_test)
            }
            
        except Exception as e:
            logger.error(f"Error training model: {str(e)}")
            raise
    
    def predict_budget(self, month: int, year: int, avg_amount: float = None, 
                      category_diversity: int = None, transaction_count: int = None) -> float:
        """Predict budget for a given month and year"""
        if not self.is_trained:
            # Return default prediction if model is not trained
            return 10000.0
        
        # Use default values if not provided
        if avg_amount is None:
            avg_amount = 2000.0
        if category_diversity is None:
            category_diversity = 5
        if transaction_count is None:
            transaction_count = 20
        
        # Prepare features
        features = np.array([[month, year, avg_amount, category_diversity, transaction_count]])
        
        try:
            prediction = self.model.predict(features)[0]
            return max(0.0, float(prediction))  # Ensure non-negative prediction
        except Exception as e:
            logger.error(f"Error making prediction: {str(e)}")
            return 10000.0  # Default fallback
    
    def save_model(self):
        """Save the trained model to disk"""
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump(self.model, self.model_path)
        logger.info(f"Model saved to {self.model_path}")
    
    def load_model(self):
        """Load a trained model from disk"""
        if os.path.exists(self.model_path):
            self.model = joblib.load(self.model_path)
            self.is_trained = True
            logger.info(f"Model loaded from {self.model_path}")
            return True
        return False
    
    def retrain_with_new_data(self, old_transactions: List[Dict], new_transactions: List[Dict]) -> Dict[str, float]:
        """Retrain model with both old and new data"""
        all_transactions = old_transactions + new_transactions
        return self.train_model(all_transactions)