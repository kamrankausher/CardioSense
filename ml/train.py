"""
CardioSense v2 — Model Training Script

Trains 3 models: Random Forest, XGBoost, Logistic Regression.
Saves models, scaler, and metrics to disk.

Interview explanation:
"I train 3 models to compare — Logistic Regression as baseline, Random Forest
for ensemble power, XGBoost for boosting. I use stratified split to preserve
class balance. Cross-validation gives a more reliable accuracy estimate."
"""

import pickle
import json
import os
import sys

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (
    classification_report, roc_auc_score,
    accuracy_score, precision_score, recall_score, f1_score
)

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ml.preprocess import load_and_clean, get_features_and_target, get_scaler


def train_all_models():
    """Train all models, evaluate, and save to disk."""
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    data_path = os.path.join(base_dir, 'data', 'heart.csv')
    models_dir = os.path.join(base_dir, 'models')

    # Ensure models directory exists
    os.makedirs(models_dir, exist_ok=True)

    print("=" * 60)
    print("CardioSense v2 — Model Training Pipeline")
    print("=" * 60)

    # Load and preprocess data
    print("\n[1/4] Loading and cleaning data...")
    df = load_and_clean(data_path)
    X, y = get_features_and_target(df)
    print(f"  Dataset: {len(df)} samples, {X.shape[1]} features")
    print(f"  Class distribution: {dict(y.value_counts())}")

    # Train-test split (stratified)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"  Train: {len(X_train)} | Test: {len(X_test)}")

    # Scale features
    print("\n[2/4] Fitting StandardScaler on training data...")
    scaler, X_train_scaled = get_scaler(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Define models
    models = {
        'random_forest': RandomForestClassifier(
            n_estimators=100, max_depth=6, random_state=42
        ),
        'xgboost': XGBClassifier(
            n_estimators=100, learning_rate=0.1, max_depth=4,
            random_state=42, eval_metric='logloss'
        ),
        'logistic_regression': LogisticRegression(
            C=1.0, max_iter=1000, random_state=42
        )
    }

    # Train and evaluate each model
    print("\n[3/4] Training models...")
    results = {}

    for name, model in models.items():
        print(f"\n  Training {name}...")
        model.fit(X_train_scaled, y_train)

        # Predictions
        y_pred = model.predict(X_test_scaled)
        y_prob = model.predict_proba(X_test_scaled)[:, 1]

        # Cross-validation
        cv_scores = cross_val_score(
            model, X_train_scaled, y_train, cv=5, scoring='accuracy'
        )

        # Metrics
        report = classification_report(y_test, y_pred, output_dict=True)
        results[name] = {
            'accuracy': round(accuracy_score(y_test, y_pred) * 100, 2),
            'auc_roc': round(roc_auc_score(y_test, y_prob), 4),
            'precision': round(precision_score(y_test, y_pred) * 100, 2),
            'recall': round(recall_score(y_test, y_pred) * 100, 2),
            'f1_score': round(f1_score(y_test, y_pred) * 100, 2),
            'cv_mean': round(cv_scores.mean() * 100, 2),
            'cv_std': round(cv_scores.std() * 100, 2),
            'report': report
        }

        print(f"    Accuracy: {results[name]['accuracy']}%")
        print(f"    AUC-ROC:  {results[name]['auc_roc']}")
        print(f"    CV Mean:  {results[name]['cv_mean']}% ± {results[name]['cv_std']}%")

        # Save model
        model_path = os.path.join(models_dir, f'{name}.pkl')
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        print(f"    Saved to: {model_path}")

    # Save scaler
    scaler_path = os.path.join(models_dir, 'scaler.pkl')
    with open(scaler_path, 'wb') as f:
        pickle.dump(scaler, f)
    print(f"\n  Scaler saved to: {scaler_path}")

    # Save metrics JSON (for model comparison page)
    metrics_path = os.path.join(models_dir, 'metrics.json')
    # Remove non-serializable report for JSON
    metrics_clean = {}
    for name, m in results.items():
        metrics_clean[name] = {k: v for k, v in m.items() if k != 'report'}
    with open(metrics_path, 'w') as f:
        json.dump(metrics_clean, f, indent=2)
    print(f"  Metrics saved to: {metrics_path}")

    print("\n" + "=" * 60)
    print("Training complete!")
    print("=" * 60)

    return results


if __name__ == '__main__':
    results = train_all_models()
