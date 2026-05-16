"""
CardioSense v2 — Prediction + SHAP Explanation

Interview explanation:
"SHAP (SHapley Additive exPlanations) is a game-theory-based method that assigns
each feature a contribution score for each individual prediction. Positive SHAP =
increases risk, negative = decreases risk. This is critical in healthcare — doctors
need to know WHY the model made a prediction, not just what the prediction is."
"""

import pickle
import os
import numpy as np
import shap

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
MODELS_DIR = os.path.join(BASE_DIR, 'models')

FEATURE_NAMES = [
    'age', 'sex', 'cp', 'trestbps', 'chol', 'fbs',
    'restecg', 'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal'
]

FEATURE_LABELS = {
    'age': 'Age',
    'sex': 'Sex',
    'cp': 'Chest Pain Type',
    'trestbps': 'Resting Blood Pressure',
    'chol': 'Cholesterol',
    'fbs': 'Fasting Blood Sugar',
    'restecg': 'Resting ECG',
    'thalach': 'Max Heart Rate',
    'exang': 'Exercise-Induced Angina',
    'oldpeak': 'ST Depression',
    'slope': 'ST Slope',
    'ca': 'Major Vessels',
    'thal': 'Thalassemia'
}


# Cache loaded models to avoid reloading on every request
_model_cache = {}
_scaler_cache = None


def load_model(model_name):
    """Load a trained model from disk (with caching)."""
    global _model_cache
    if model_name not in _model_cache:
        model_path = os.path.join(MODELS_DIR, f'{model_name}.pkl')
        with open(model_path, 'rb') as f:
            _model_cache[model_name] = pickle.load(f)
    return _model_cache[model_name]


def load_scaler():
    """Load the fitted scaler from disk (with caching)."""
    global _scaler_cache
    if _scaler_cache is None:
        scaler_path = os.path.join(MODELS_DIR, 'scaler.pkl')
        with open(scaler_path, 'rb') as f:
            _scaler_cache = pickle.load(f)
    return _scaler_cache


def predict_single(form_data, model_name='random_forest'):
    """
    Make a single prediction with SHAP explanations.

    Args:
        form_data: dict with feature keys and values
        model_name: one of 'random_forest', 'xgboost', 'logistic_regression'

    Returns:
        dict with prediction, probability, risk level, SHAP contributions
    """
    model = load_model(model_name)
    scaler = load_scaler()

    # Build input array in correct feature order
    input_values = [float(form_data[feat]) for feat in FEATURE_NAMES]
    input_array = np.array(input_values).reshape(1, -1)
    input_scaled = scaler.transform(input_array)

    # Prediction
    prediction = int(model.predict(input_scaled)[0])
    probability = float(model.predict_proba(input_scaled)[0][1])

    # Risk level classification
    if probability < 0.3:
        risk_level = 'Low'
        risk_color = '#22c55e'
    elif probability < 0.6:
        risk_level = 'Moderate'
        risk_color = '#f59e0b'
    else:
        risk_level = 'High'
        risk_color = '#ef4444'

    # SHAP explanation
    if model_name == 'logistic_regression':
        explainer = shap.LinearExplainer(model, input_scaled)
    else:
        explainer = shap.TreeExplainer(model)

    shap_values = explainer.shap_values(input_scaled)

    # Handle different SHAP output formats
    if isinstance(shap_values, list):
        # Binary classification: list of [class_0, class_1]
        shap_for_class1 = shap_values[1][0]
    elif len(shap_values.shape) == 3:
        shap_for_class1 = shap_values[0, :, 1]
    else:
        shap_for_class1 = shap_values[0]

    # Build SHAP feature contributions list
    shap_contributions = []
    for i, feat in enumerate(FEATURE_NAMES):
        shap_contributions.append({
            'feature': FEATURE_LABELS[feat],
            'feature_key': feat,
            'value': input_values[i],
            'shap_value': round(float(shap_for_class1[i]), 4),
            'direction': 'increases' if shap_for_class1[i] > 0 else 'decreases'
        })

    # Sort by absolute SHAP value (most important first)
    shap_contributions.sort(key=lambda x: abs(x['shap_value']), reverse=True)

    return {
        'prediction': prediction,
        'probability': round(probability * 100, 1),
        'risk_level': risk_level,
        'risk_color': risk_color,
        'model_used': model_name,
        'shap_contributions': shap_contributions[:8],  # Top 8 features
        'input_values': dict(zip(FEATURE_NAMES, input_values))
    }
