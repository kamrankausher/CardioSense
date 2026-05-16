"""
CardioSense v2 — PDF Report Generator

Generates professional medical-style PDF reports using ReportLab.

Interview explanation:
"ReportLab lets me build PDFs programmatically using a 'flowable' concept —
each section is an independent block that flows into the page. I use SHAP values
directly in the report so doctors can see which clinical features drove the
prediction, making it auditable and trustworthy."
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
import json
import os


def generate_pdf_report(record):
    """Generate a clean medical-style PDF report for a prediction result."""

    # Output path
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    output_dir = os.path.join(base_dir, 'reports', 'output')
    os.makedirs(output_dir, exist_ok=True)
    pdf_path = os.path.join(output_dir, f'report_{record.id}.pdf')

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle', parent=styles['Heading1'],
        fontSize=22, textColor=colors.HexColor('#1e40af'),
        spaceAfter=6, alignment=TA_CENTER
    )
    subtitle_style = ParagraphStyle(
        'CustomSubtitle', parent=styles['Normal'],
        fontSize=11, textColor=colors.HexColor('#6b7280'),
        spaceAfter=20, alignment=TA_CENTER
    )
    section_style = ParagraphStyle(
        'CustomSection', parent=styles['Heading2'],
        fontSize=13, textColor=colors.HexColor('#1e293b'),
        spaceBefore=16, spaceAfter=8, borderPad=4
    )
    body_style = ParagraphStyle(
        'CustomBody', parent=styles['Normal'],
        fontSize=10, textColor=colors.HexColor('#374151'),
        spaceAfter=6, leading=16
    )

    # Parse stored JSON
    input_data = json.loads(record.input_data)
    shap_data = json.loads(record.shap_data)

    # Risk colors
    risk_colors = {
        'Low': colors.HexColor('#166534'),
        'Moderate': colors.HexColor('#92400e'),
        'High': colors.HexColor('#991b1b')
    }
    risk_bg_colors = {
        'Low': colors.HexColor('#dcfce7'),
        'Moderate': colors.HexColor('#fef3c7'),
        'High': colors.HexColor('#fee2e2')
    }
    risk_color = risk_colors.get(record.risk_level, colors.black)
    risk_bg = risk_bg_colors.get(record.risk_level, colors.white)

    story = []

    # --- HEADER ---
    story.append(Paragraph("CardioSense AI", title_style))
    story.append(Paragraph("Heart Disease Risk Assessment Report", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1,
                            color=colors.HexColor('#e5e7eb')))
    story.append(Spacer(1, 0.3 * inch))

    # --- PATIENT INFO ---
    story.append(Paragraph("Patient Information", section_style))

    created_str = record.created_at.strftime('%d %B %Y') if record.created_at else 'N/A'
    patient_data = [
        ['Patient Name', record.patient_name or 'Anonymous',
         'Assessment Date', created_str],
        ['Age', f"{record.age} years",
         'Model Used', record.model_used.replace('_', ' ').title()],
    ]
    patient_table = Table(patient_data, colWidths=[3.5 * cm, 5.5 * cm, 3.5 * cm, 5.5 * cm])
    patient_table.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#6b7280')),
        ('TEXTCOLOR', (2, 0), (2, -1), colors.HexColor('#6b7280')),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
        ('FONTNAME', (3, 0), (3, -1), 'Helvetica-Bold'),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1),
         [colors.HexColor('#f9fafb'), colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(patient_table)
    story.append(Spacer(1, 0.25 * inch))

    # --- RISK RESULT ---
    story.append(Paragraph("Assessment Result", section_style))

    result_text = ("Heart Disease Detected" if record.prediction == 1
                   else "No Heart Disease Detected")

    risk_data = [
        [Paragraph(f'<b>{result_text}</b>', ParagraphStyle(
            'RiskTitle', fontSize=14, textColor=risk_color, alignment=TA_CENTER
        ))],
        [Paragraph(f'Risk Level: <b>{record.risk_level}</b>  |  '
                   f'Probability: <b>{record.probability:.1f}%</b>',
                   ParagraphStyle('RiskSub', fontSize=11,
                                  textColor=risk_color, alignment=TA_CENTER))]
    ]
    risk_table = Table(risk_data, colWidths=[17 * cm])
    risk_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), risk_bg),
        ('PADDING', (0, 0), (-1, -1), 12),
        ('BOX', (0, 0), (-1, -1), 1, risk_color),
    ]))
    story.append(risk_table)
    story.append(Spacer(1, 0.25 * inch))

    # --- TOP CONTRIBUTING FACTORS (SHAP) ---
    story.append(Paragraph("Top Risk Contributing Factors", section_style))
    story.append(Paragraph(
        "The following features had the most influence on this prediction, "
        "based on SHAP (SHapley Additive exPlanations) values:",
        body_style
    ))

    shap_header = [['Feature', 'Patient Value', 'Influence', 'Effect on Risk']]
    shap_rows = []
    for item in shap_data[:8]:
        direction_text = ('▲ Increases risk' if item['direction'] == 'increases'
                          else '▼ Decreases risk')
        direction_color = (colors.HexColor('#991b1b') if item['direction'] == 'increases'
                           else colors.HexColor('#166534'))
        shap_rows.append([
            item['feature'],
            str(item['value']),
            f"{item['shap_value']:+.4f}",
            Paragraph(direction_text, ParagraphStyle(
                'Dir', fontSize=9, textColor=direction_color
            ))
        ])

    shap_table_data = shap_header + shap_rows
    shap_table = Table(shap_table_data, colWidths=[5 * cm, 3.5 * cm, 3.5 * cm, 5 * cm])
    shap_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1),
         [colors.HexColor('#f8fafc'), colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('ALIGN', (2, 0), (2, -1), 'CENTER'),
    ]))
    story.append(shap_table)
    story.append(Spacer(1, 0.25 * inch))

    # --- INPUT VALUES TABLE ---
    story.append(Paragraph("Clinical Input Values", section_style))

    feature_labels = {
        'age': 'Age', 'sex': 'Sex (1=Male)', 'cp': 'Chest Pain Type',
        'trestbps': 'Resting BP (mmHg)', 'chol': 'Cholesterol (mg/dl)',
        'fbs': 'Fasting Blood Sugar', 'restecg': 'Resting ECG',
        'thalach': 'Max Heart Rate', 'exang': 'Exercise Angina',
        'oldpeak': 'ST Depression', 'slope': 'ST Slope',
        'ca': 'Major Vessels', 'thal': 'Thalassemia'
    }

    input_rows = []
    items = list(input_data.items())
    for i in range(0, len(items), 2):
        row = []
        row.append(feature_labels.get(items[i][0], items[i][0]))
        row.append(str(items[i][1]))
        if i + 1 < len(items):
            row.append(feature_labels.get(items[i + 1][0], items[i + 1][0]))
            row.append(str(items[i + 1][1]))
        else:
            row.extend(['', ''])
        input_rows.append(row)

    input_table = Table(input_rows, colWidths=[4.5 * cm, 4 * cm, 4.5 * cm, 4 * cm])
    input_table.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#6b7280')),
        ('TEXTCOLOR', (2, 0), (2, -1), colors.HexColor('#6b7280')),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1),
         [colors.HexColor('#f9fafb'), colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(input_table)
    story.append(Spacer(1, 0.25 * inch))

    # --- DISCLAIMER ---
    story.append(HRFlowable(width="100%", thickness=0.5,
                            color=colors.HexColor('#e5e7eb')))
    story.append(Spacer(1, 0.15 * inch))
    disclaimer_style = ParagraphStyle(
        'Disclaimer', parent=styles['Normal'],
        fontSize=8, textColor=colors.HexColor('#9ca3af'),
        alignment=TA_CENTER, leading=12
    )
    story.append(Paragraph(
        "This report is generated by CardioSense AI for educational and research "
        "purposes only. It is NOT a substitute for professional medical advice, "
        "diagnosis, or treatment. Always consult a qualified healthcare provider "
        "for medical decisions.",
        disclaimer_style
    ))

    doc.build(story)
    return pdf_path
