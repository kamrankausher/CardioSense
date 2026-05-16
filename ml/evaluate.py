"""
CardioSense v2 — Model Evaluation & Comparison

Provides utilities for evaluating and comparing trained models.
"""

import pickle
import os
import json
import numpy as np
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, confusion_matrix
)
from sklearn.model_selection import cross_val_score

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


def load_metrics():
    """Load pre-computed model metrics from disk."""
    metrics_path = os.path.join(BASE_DIR, 'models', 'metrics.json')
    if not os.path.exists(metrics_path):
        return None
    with open(metrics_path, 'r') as f:
        return json.load(f)


def get_model_comparison():
    """Return a formatted comparison of all models."""
    metrics = load_metrics()
    if not metrics:
        return None

    comparison = []
    for name, m in metrics.items():
        comparison.append({
            'model': name.replace('_', ' ').title(),
            'model_key': name,
            'accuracy': m['accuracy'],
            'auc_roc': m['auc_roc'],
            'precision': m['precision'],
            'recall': m['recall'],
            'f1_score': m['f1_score'],
            'cv_mean': m['cv_mean'],
            'cv_std': m['cv_std']
        })

    return comparison
