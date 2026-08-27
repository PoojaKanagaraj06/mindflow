import os
import pickle

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.model_selection import train_test_split

from ml.predict import MODEL_PATH


TRAINING_DATA = [
    ("read novel", "Low", "Pending", "Personal", 2, 20, 0.12),
    ("buy groceries", "Low", "Pending", "Personal", 1, 3, 0.31),
    ("plan vacation", "Medium", "Pending", "Personal", 5, 14, 0.43),
    ("prepare weekly report", "Medium", "In Progress", "Work", 3, 4, 0.64),
    ("schedule dentist appointment", "Medium", "Pending", "Health", 1, 2, 0.62),
    ("submit tax documents", "High", "Pending", "Finance", 4, 3, 0.91),
    ("fix production outage", "High", "In Progress", "Work", 2, 0, 1.0),
    ("complete project report", "High", "In Progress", "Work", 8, 2, 0.94),
    ("renew passport", "High", "Pending", "Admin", 2, 10, 0.77),
    ("organize photo library", "Low", "Pending", "Personal", 6, 30, 0.08),
    ("review security incident", "High", "In Progress", "Security", 3, 1, 0.98),
    ("write marketing brief", "Medium", "Pending", "Work", 4, 7, 0.70),
    ("book flight tickets", "High", "Pending", "Travel", 2, 5, 0.82),
    ("water plants", "Low", "Pending", "Home", 0.5, 1, 0.25),
    ("finish urgent client proposal", "High", "In Progress", "Work", 6, 1, 0.99),
    ("learn guitar chords", "Low", "Pending", "Personal", 3, 60, 0.04),
]


def train():
    feature_rows = []
    scores = []
    labels = []
    for task_name, priority, status, category, estimated_time, days_remaining, score in TRAINING_DATA:
        feature_rows.append({
            "task_name": task_name,
            "priority": priority,
            "status": status,
            "category": category,
            "estimated_time": estimated_time,
            "days_remaining": days_remaining,
            "urgency": max(0, 30 - days_remaining) / 30,
        })
        scores.append(score)
        labels.append("High" if score >= 0.70 else "Medium" if score >= 0.40 else "Low")

    preprocessor = ColumnTransformer([
        ("text", TfidfVectorizer(ngram_range=(1, 2)), "task_name"),
        ("categories", OneHotEncoder(handle_unknown="ignore"), ["priority", "status", "category"]),
    ], remainder="passthrough")
    regressor = Pipeline([("preprocessor", preprocessor), ("model", RandomForestRegressor(n_estimators=120, random_state=42))])
    classifier = Pipeline([("preprocessor", preprocessor), ("model", RandomForestClassifier(n_estimators=120, random_state=42))])
    feature_frame = pd.DataFrame(feature_rows)
    train_features, test_features, train_scores, test_scores, train_labels, test_labels = train_test_split(
        feature_frame, scores, labels, test_size=0.25, random_state=42, stratify=labels
    )
    regressor.fit(train_features, train_scores)
    classifier.fit(train_features, train_labels)
    print(f"Regression R2: {r2_score(test_scores, regressor.predict(test_features)):.2f}")
    print(f"Classification accuracy: {accuracy_score(test_labels, classifier.predict(test_features)):.2f}")
    regressor.fit(feature_frame, scores)
    classifier.fit(feature_frame, labels)
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    with open(MODEL_PATH, "wb") as model_file:
        pickle.dump({"regressor": regressor, "classifier": classifier}, model_file)
    print(f"Saved trained model to {MODEL_PATH}")


if __name__ == "__main__":
    train()