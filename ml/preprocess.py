"""
CardioSense v2 — Data Preprocessing Pipeline

Interview explanation:
"I use IQR clipping instead of removing outliers to preserve data.
StandardScaler is needed because features like age (20-80) and cholesterol (100-600)
are on very different scales — it prevents the model from being biased toward
high-magnitude features."
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler


def load_and_clean(filepath):
    """Load the heart disease dataset and perform cleaning."""
    df = pd.read_csv(filepath)

    # Drop duplicates and nulls
    df.drop_duplicates(inplace=True)
    df.dropna(inplace=True)

    # Clip outliers using IQR method for continuous features
    for col in ['trestbps', 'chol', 'thalach', 'oldpeak']:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        df[col] = df[col].clip(Q1 - 1.5 * IQR, Q3 + 1.5 * IQR)

    return df


def get_features_and_target(df):
    """Split dataframe into features (X) and target (y)."""
    X = df.drop('target', axis=1)
    y = df['target']
    return X, y


def get_scaler(X_train):
    """Fit a StandardScaler on training data only (prevents data leakage)."""
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_train)
    return scaler, X_scaled
