"""
CardioSense v2 — Flask Application

Main application entry point with all routes.
"""

from flask import Flask, render_template, request, jsonify, send_file
import json
import os
import io
from datetime import datetime

from database.models import db, PatientRecord
from ml.predict import predict_single
from reports.generator import generate_pdf_report


def create_app():
    """Application factory pattern."""
    app = Flask(__name__)

    # Configuration
    base_dir = os.path.abspath(os.path.dirname(__file__))
    db_dir = os.path.join(base_dir, 'database')
    os.makedirs(db_dir, exist_ok=True)

    app.config['SECRET_KEY'] = 'cardiosense-dev-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(db_dir, 'cardiosense.db')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize database
    db.init_app(app)

    with app.app_context():
        db.create_all()

    # ── Routes ──────────────────────────────────────────────────

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/predict')
    def predict_page():
        return render_template('predict.html')

    @app.route('/api/predict', methods=['POST'])
    def api_predict():
        """Main prediction endpoint — called by JavaScript fetch()"""
        try:
            form_data = request.get_json()
            model_name = form_data.pop('model_name', 'random_forest')
            patient_name = form_data.pop('patient_name', 'Anonymous')

            result = predict_single(form_data, model_name)

            # Save to database
            record = PatientRecord(
                patient_name=patient_name if patient_name else 'Anonymous',
                age=int(form_data.get('age', 0)),
                prediction=result['prediction'],
                probability=result['probability'],
                risk_level=result['risk_level'],
                model_used=model_name,
                input_data=json.dumps(form_data),
                shap_data=json.dumps(result['shap_contributions'])
            )
            db.session.add(record)
            db.session.commit()

            result['record_id'] = record.id
            return jsonify({'success': True, 'data': result})

        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/result/<int:record_id>')
    def result_page(record_id):
        record = PatientRecord.query.get_or_404(record_id)
        return render_template('result.html', record=record)

    @app.route('/api/report/<int:record_id>')
    def download_report(record_id):
        """Generate and download PDF report."""
        record = PatientRecord.query.get_or_404(record_id)
        pdf_path = generate_pdf_report(record)
        return send_file(
            pdf_path, as_attachment=True,
            download_name=f'CardioSense_Report_{record_id}.pdf'
        )

    @app.route('/dashboard')
    def dashboard():
        records = PatientRecord.query.order_by(
            PatientRecord.created_at.desc()
        ).all()
        stats = {
            'total': len(records),
            'high_risk': sum(1 for r in records if r.risk_level == 'High'),
            'moderate_risk': sum(1 for r in records if r.risk_level == 'Moderate'),
            'low_risk': sum(1 for r in records if r.risk_level == 'Low'),
        }
        return render_template('dashboard.html', records=records, stats=stats)

    @app.route('/api/dashboard/chart-data')
    def dashboard_chart_data():
        """Return JSON data for dashboard charts."""
        records = PatientRecord.query.all()

        # Risk distribution
        risk_counts = {'Low': 0, 'Moderate': 0, 'High': 0}
        for r in records:
            if r.risk_level in risk_counts:
                risk_counts[r.risk_level] += 1

        # Age data
        age_data = [
            {'age': r.age, 'risk': r.risk_level, 'prob': r.probability}
            for r in records
        ]

        # Model usage
        model_counts = {}
        for r in records:
            model_counts[r.model_used] = model_counts.get(r.model_used, 0) + 1

        # Timeline (last 30 predictions)
        timeline_data = []
        for r in records[-30:]:
            timeline_data.append({
                'date': r.created_at.strftime('%Y-%m-%d %H:%M') if r.created_at else '',
                'probability': r.probability,
                'risk': r.risk_level
            })

        return jsonify({
            'risk_distribution': risk_counts,
            'age_data': age_data,
            'model_usage': model_counts,
            'total_predictions': len(records),
            'timeline': timeline_data
        })

    @app.route('/compare')
    def compare_page():
        return render_template('compare.html')

    @app.route('/api/model-metrics')
    def model_metrics():
        """Return pre-computed model performance metrics."""
        try:
            metrics_path = os.path.join(base_dir, 'models', 'metrics.json')
            with open(metrics_path, 'r') as f:
                metrics = json.load(f)
            return jsonify({'success': True, 'data': metrics})
        except FileNotFoundError:
            return jsonify({
                'success': False,
                'error': 'Models not trained yet. Run: python ml/train.py'
            }), 404

    @app.route('/batch')
    def batch_page():
        return render_template('batch.html')

    @app.route('/api/batch-predict', methods=['POST'])
    def batch_predict():
        """Batch prediction from uploaded CSV."""
        import pandas as pd

        file = request.files.get('file')
        if not file:
            return jsonify({'success': False, 'error': 'No file uploaded'}), 400

        try:
            df = pd.read_csv(io.StringIO(file.read().decode('utf-8')))

            results = []
            for _, row in df.iterrows():
                result = predict_single(row.to_dict(), 'random_forest')
                results.append({
                    'risk_level': result['risk_level'],
                    'probability': result['probability'],
                    'prediction': result['prediction'],
                    'age': int(row.get('age', 0)),
                })

            return jsonify({
                'success': True,
                'results': results,
                'count': len(results)
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/records/<int:record_id>')
    def get_record(record_id):
        """Get a single record as JSON."""
        record = PatientRecord.query.get_or_404(record_id)
        return jsonify({
            'id': record.id,
            'patient_name': record.patient_name,
            'age': record.age,
            'prediction': record.prediction,
            'probability': record.probability,
            'risk_level': record.risk_level,
            'model_used': record.model_used,
            'input_data': json.loads(record.input_data),
            'shap_data': json.loads(record.shap_data),
            'created_at': record.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
