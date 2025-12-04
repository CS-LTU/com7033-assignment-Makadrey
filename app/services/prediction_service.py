"""
Prediction Service
==================

Business logic for ML stroke risk prediction.
"""

import pickle
import numpy as np
import os
import logging
from flask import current_app


class PredictionService:
    """Service class for stroke risk prediction."""
    
    _instance = None
    _model = None
    _scaler = None
    _label_encoders = None
    
    def __new__(cls):
        """Singleton pattern for model loading efficiency."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def load_model(self):
        """Load pre-trained model, scaler, and encoders."""
        if self._model is not None:
            return True
        
        try:
            # Try multiple possible paths
            model_paths = [
                current_app.config.get('MODEL_PATH', 'ml_models/stroke_model.pkl'),
                'stroke_model.pkl',
                'ml_models/stroke_model.pkl'
            ]
            
            scaler_paths = [
                current_app.config.get('SCALER_PATH', 'ml_models/scaler.pkl'),
                'scaler.pkl',
                'ml_models/scaler.pkl'
            ]
            
            encoder_paths = [
                current_app.config.get('ENCODERS_PATH', 'ml_models/label_encoders.pkl'),
                'label_encoders.pkl',
                'ml_models/label_encoders.pkl'
            ]
            
            # Load model
            for path in model_paths:
                if os.path.exists(path):
                    self._model = pickle.load(open(path, 'rb'))
                    logging.info(f"Loaded model from {path}")
                    break
            
            # Load scaler
            for path in scaler_paths:
                if os.path.exists(path):
                    self._scaler = pickle.load(open(path, 'rb'))
                    logging.info(f"Loaded scaler from {path}")
                    break
            
            # Load encoders
            for path in encoder_paths:
                if os.path.exists(path):
                    self._label_encoders = pickle.load(open(path, 'rb'))
                    logging.info(f"Loaded encoders from {path}")
                    break
            
            if self._model and self._scaler and self._label_encoders:
                logging.info("ML model loaded successfully")
                return True
            else:
                logging.warning("Some model files not found")
                return False
                
        except Exception as e:
            logging.error(f"Error loading model: {e}")
            return False
    
    def predict_risk(self, patient_data):
        """
        Predict stroke risk for a patient.
        
        Args:
            patient_data (dict): Patient features including:
                - gender, age, hypertension, heart_disease
                - ever_married, work_type, Residence_type
                - avg_glucose_level, bmi, smoking_status
                
        Returns:
            dict: Prediction result with:
                - success (bool)
                - risk_probability (float): Percentage
                - risk_category (str): Low/Medium/High Risk
                - risk_color (str): green/orange/red
                - error (str): Error message if failed
        """
        if not self.load_model():
            return {'success': False, 'error': 'Model not loaded'}
        
        if self._model is None:
            return {'success': False, 'error': 'Model not available'}
        
        try:
            # Encode categorical variables
            encoded_data = patient_data.copy()
            categorical_cols = ['gender', 'ever_married', 'work_type', 'Residence_type', 'smoking_status']
            
            for col in categorical_cols:
                if col in self._label_encoders and col in patient_data:
                    try:
                        encoded_data[col] = self._label_encoders[col].transform([patient_data[col]])[0]
                    except ValueError:
                        # Handle unseen labels
                        logging.warning(f"Unseen label for {col}: {patient_data[col]}")
                        encoded_data[col] = 0
            
            # Create feature array in correct order
            feature_order = [
                'gender', 'age', 'hypertension', 'heart_disease', 
                'ever_married', 'work_type', 'Residence_type', 
                'avg_glucose_level', 'bmi', 'smoking_status'
            ]
            
            X_input = np.array([[encoded_data[col] for col in feature_order]])
            
            # Scale and predict
            X_scaled = self._scaler.transform(X_input)
            risk_probability = self._model.predict_proba(X_scaled)[0][1]
            
            # Categorize risk
            if risk_probability < 0.33:
                risk_category = "Low Risk"
                risk_color = "green"
            elif risk_probability < 0.66:
                risk_category = "Medium Risk"
                risk_color = "orange"
            else:
                risk_category = "High Risk"
                risk_color = "red"
            
            return {
                'success': True,
                'risk_probability': round(risk_probability * 100, 2),
                'risk_category': risk_category,
                'risk_color': risk_color
            }
        
        except Exception as e:
            logging.error(f"Prediction error: {e}")
            return {'success': False, 'error': str(e)}


# Global instance
prediction_service = PredictionService()

