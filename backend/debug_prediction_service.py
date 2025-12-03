import sys
import os
from sqlalchemy.orm import Session

# Add app directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from app.config.database import SessionLocal
    from app.services.prediction_service import PredictionService
    from app.models.user import User
    
    print("Connecting to DB...")
    db = SessionLocal()
    
    # Get a user (ID 1)
    user = db.query(User).first()
    if not user:
        print("No users found in DB.")
        exit(1)
    
    print(f"Using User ID: {user.id}")
    
    print("Initializing PredictionService...")
    service = PredictionService(db)
    
    print("Calling predict_next_month_budget...")
    result = service.predict_next_month_budget(user.id)
    print("Result:", result)

except Exception as e:
    print("CRASHED:")
    import traceback
    traceback.print_exc()
finally:
    if 'db' in locals():
        db.close()
