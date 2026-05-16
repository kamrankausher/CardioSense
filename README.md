# 🫀 CardioSense AI

A production-quality heart disease prediction web application built with Flask, scikit-learn, and Vanilla HTML/CSS/JS. CardioSense AI leverages multiple machine learning models to assess cardiovascular risk based on clinical data, providing explainable AI (XAI) insights using SHAP and generating medical-style PDF reports.

![CardioSense AI Dashboard](screenshots/dashboard.png) *(Note: Screenshots directory to be populated)*

## ✨ Features

*   **Intelligent Prediction Engine:** Supports multiple ML models including Random Forest (recommended), XGBoost, and Logistic Regression.
*   **Explainable AI (XAI):** Integrates SHAP (SHapley Additive exPlanations) to dynamically visualize feature importance for every individual prediction, building trust in clinical settings.
*   **Analytics Dashboard:** Interactive charts built with Chart.js showing demographic distributions, risk by age, and feature correlations based on past predictions.
*   **Model Comparison:** Dedicated view to compare the accuracy, precision, recall, and F1-scores of the trained models.
*   **Batch Processing:** Drag-and-drop CSV upload for processing multiple patient records simultaneously.
*   **Clinical PDF Reports:** Generates professional, downloadable PDF reports using `reportlab`.
*   **Premium UI/UX:** Clean, responsive, glassmorphism-inspired design using pure Vanilla HTML, CSS, and JS (no bulky frontend frameworks).

## 🛠️ Tech Stack

*   **Backend:** Python 3, Flask, SQLAlchemy (SQLite)
*   **Machine Learning:** scikit-learn, XGBoost, pandas, numpy
*   **Explainability:** SHAP
*   **Frontend:** Vanilla HTML5, CSS3, JavaScript (ES6+), Chart.js (via CDN)
*   **Reporting:** ReportLab

## 🚀 Getting Started

### Prerequisites
*   Python 3.8+
*   Git

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/kamrankausher/CardioSense.git
    cd CardioSense
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # Windows
    python -m venv venv
    venv\Scripts\activate

    # macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Train the Machine Learning Models:**
    Before running the app, you need to generate the model artifacts (`.pkl` files). The dataset is included in `data/heart.csv`.
    ```bash
    python ml/train.py
    ```

5.  **Run the Flask Application:**
    ```bash
    python app.py
    ```

6.  **Access the Application:**
    Open your browser and navigate to `http://127.0.0.1:5000`

## 📂 Project Structure

```text
CardioSense/
├── app.py                  # Main Flask application entry point
├── config.py               # Configuration settings
├── requirements.txt        # Python dependencies
├── data/
│   └── heart.csv           # UCI Heart Disease dataset
├── database/
│   ├── __init__.py
│   └── models.py           # SQLAlchemy database models
├── ml/
│   ├── __init__.py
│   ├── evaluate.py         # Model evaluation logic
│   ├── predict.py          # Prediction and SHAP logic
│   ├── preprocess.py       # Data cleaning and scaling
│   └── train.py            # Model training script
├── models/                 # Generated .pkl models and metrics
│   └── metrics.json        # Training performance metrics
├── reports/
│   ├── __init__.py
│   └── generator.py        # ReportLab PDF generation
├── static/                 # Frontend assets
│   ├── assets/             # Images and icons
│   ├── css/                # Vanilla CSS styles
│   └── js/                 # Vanilla JavaScript
└── templates/              # Jinja2 HTML templates
    ├── base.html           # Shared layout
    ├── index.html          # Landing page
    ├── predict.html        # Prediction form
    ├── result.html         # Prediction results & SHAP
    ├── dashboard.html      # Analytics dashboard
    ├── compare.html        # Model comparison
    └── batch.html          # CSV batch upload
```

## 📄 License
This project is intended for educational and portfolio demonstration purposes. Not for actual medical diagnostic use.
