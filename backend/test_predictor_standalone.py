import sys
import os

# Add app directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    print("Importing BudgetPredictor...")
    from app.ml.predictor import BudgetPredictor
    print("Import successful.")

    print("Initializing BudgetPredictor...")
    predictor = BudgetPredictor("app/ml/models/budget_predictor.pkl")
    print("Initialization successful.")

    print("Loading model...")
    loaded = predictor.load_model()
    print(f"Model loaded: {loaded}")

    print("Making prediction...")
    pred = predictor.predict_budget(1, 2026)
    print(f"Prediction: {pred}")

except Exception as e:
    print(f"CRASHED: {e}")
    import traceback
    traceback.print_exc()
