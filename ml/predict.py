import os
import pickle
from datetime import date

import pandas as pd


MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")


def _features(task):
    days_remaining = (task.deadline - date.today()).days
    return {











































































































        
        "task_name": task.task_name,
        "priority": task.priority,
        "status": task.status,
        "category": task.category,
        "estimated_time": task.estimated_time,
        "days_remaining": days_remaining,
        "urgency": max(0, 30 - days_remaining) / 30,
    }


def predict_task(task):
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError("ML model is not trained. Run: python -m ml.train_model")
    with open(MODEL_PATH, "rb") as model_file:
        artifacts = pickle.load(model_file)
    features = _features(task)
    feature_frame = pd.DataFrame([features])
    score = float(artifacts["regressor"].predict(feature_frame)[0])
    score = max(0.0, min(1.0, score))
    predicted_priority = artifacts["classifier"].predict(feature_frame)[0]
    return {"priority_score": round(score, 2), "predicted_priority": predicted_priority}