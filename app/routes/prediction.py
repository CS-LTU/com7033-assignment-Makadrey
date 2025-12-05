"""
Prediction Routes
=================

ML stroke risk prediction endpoints.
"""

import logging
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required

from app.services.prediction_service import prediction_service
from app.utils.validators import validate_prediction_input


prediction_bp = Blueprint('prediction', __name__)


@prediction_bp.route('/predict-page')
@login_required
def predict_page():
    """
    Display stroke prediction form page.
    """
    return render_template('prediction/form.html')


@prediction_bp.route('/predict', methods=['POST'])
@login_required
def predict():
    """
    Predict stroke risk for a patient.
    
    Expects JSON body with patient data.
    Returns JSON with prediction result.
    """
    try:
        data = request.json
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Validate input
        is_valid, error_msg = validate_prediction_input(data)
        if not is_valid:
            return jsonify({'success': False, 'error': error_msg}), 400
        
        # Prepare patient data
        patient_data = {
            'gender': data.get('gender'),
            'age': float(data.get('age')),
            'hypertension': int(data.get('hypertension', 0)),
            'heart_disease': int(data.get('heart_disease', 0)),
            'ever_married': data.get('ever_married'),
            'work_type': data.get('work_type'),
            'Residence_type': data.get('Residence_type'),
            'avg_glucose_level': float(data.get('avg_glucose_level')),
            'bmi': float(data.get('bmi')),
            'smoking_status': data.get('smoking_status')
        }
        
        # Get prediction
        result = prediction_service.predict_risk(patient_data)
        
        if result.get('success'):
            logging.info(
                f"Prediction: {result['risk_category']} ({result['risk_probability']}%)"
            )
        
        return jsonify(result)
    
    except ValueError as e:
        logging.error(f"Prediction validation error: {e}")
        return jsonify({'success': False, 'error': f'Invalid input: {str(e)}'}), 400
    
    except Exception as e:
        logging.error(f"Prediction error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

