"""
CardioSense v2 — Database Models

SQLAlchemy ORM model for patient prediction records.

Interview explanation:
"SQLite is perfect for a portfolio project — zero setup, file-based, ships with Python.
I'd switch to PostgreSQL for production. The SQLAlchemy ORM abstracts the database
so swapping is one config line change."
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class PatientRecord(db.Model):
    """Stores each prediction result for the patient history dashboard."""
    __tablename__ = 'patient_records'

    id = db.Column(db.Integer, primary_key=True)
    patient_name = db.Column(db.String(100), default='Anonymous')
    age = db.Column(db.Integer)
    prediction = db.Column(db.Integer)          # 0 or 1
    probability = db.Column(db.Float)           # 0-100 percentage
    risk_level = db.Column(db.String(20))       # Low / Moderate / High
    model_used = db.Column(db.String(50))       # random_forest, xgboost, etc.
    input_data = db.Column(db.Text)             # JSON string of input features
    shap_data = db.Column(db.Text)              # JSON string of SHAP contributions
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<PatientRecord {self.id} - {self.patient_name} - {self.risk_level}>"
