import os
import pickle
import pandas as pd
from typing import Dict, Any

class RecoveryPredictor:
    def __init__(self):
        model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models", "recovery_model.pkl")
        self.model = None
        self.model_version = "v1.0-lr"
        
        if os.path.exists(model_path):
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
                
    def predict(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Accepts raw case data and predicts recovery probability.
        Applies the same preprocessing pipeline used during training.
        """
        if not self.model:
            return {
                "recovery_probability": 0.0,
                "prediction": 0,
                "model_version": "none",
                "error": "Model file not found"
            }
            
        # Create DataFrame for single row
        df = pd.DataFrame([case_data])
        
        try:
            # The pipeline handles preprocessing and scaling internally
            prediction = self.model.predict(df)[0]
            probability = self.model.predict_proba(df)[0][1]
            
            return {
                "recovery_probability": float(probability),
                "prediction": int(prediction),
                "model_version": self.model_version
            }
        except Exception as e:
            return {
                "recovery_probability": 0.0,
                "prediction": 0,
                "model_version": self.model_version,
                "error": str(e)
            }
