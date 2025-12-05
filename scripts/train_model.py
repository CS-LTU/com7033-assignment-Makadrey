"""
Stroke Prediction Model Training Script
========================================

This script trains the Random Forest model for stroke risk prediction.
Run this script to retrain the model with updated data.

Usage:
    python scripts/train_model.py

Output:
    - ml_models/stroke_model.pkl
    - ml_models/scaler.pkl
    - ml_models/label_encoders.pkl
"""

import os
import sys
import pickle
import warnings
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
from sklearn.utils.class_weight import compute_class_weight

warnings.filterwarnings('ignore')

# Paths
DATA_PATH = 'data/healthcare-dataset-stroke-data.csv'
MODEL_PATH = 'ml_models/stroke_model.pkl'
SCALER_PATH = 'ml_models/scaler.pkl'
ENCODERS_PATH = 'ml_models/label_encoders.pkl'


def load_and_preprocess_data(filepath):
    """Load and preprocess the stroke dataset."""
    print(f"Loading data from {filepath}...")
    df = pd.read_csv(filepath)
    
    print("=" * 60)
    print("STROKE PREDICTION MODEL - DATA OVERVIEW")
    print("=" * 60)
    print(f"Total patients: {len(df)}")
    print(f"Stroke cases: {df['stroke'].sum()}")
    print(f"Non-stroke cases: {(df['stroke'] == 0).sum()}")
    print(f"Stroke percentage: {(df['stroke'].sum() / len(df) * 100):.2f}%\n")
    
    # Data preprocessing
    df['bmi'] = pd.to_numeric(df['bmi'], errors='coerce')
    df['bmi'].fillna(df['bmi'].median(), inplace=True)
    df['smoking_status'].fillna('Unknown', inplace=True)
    
    # Handle missing values
    df = df.dropna(subset=['gender'])
    
    return df


def encode_categorical(df):
    """Encode categorical variables."""
    le_dict = {}
    categorical_cols = ['gender', 'ever_married', 'work_type', 'Residence_type', 'smoking_status']
    
    for col in categorical_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])
        le_dict[col] = le
    
    return df, le_dict


def train_model(X_train, y_train):
    """Train the Random Forest model."""
    # Compute class weights to handle imbalance
    class_weights = compute_class_weight(
        'balanced',
        classes=np.unique(y_train),
        y=y_train
    )
    class_weight_dict = {0: class_weights[0], 1: class_weights[1]}
    
    print("Training Random Forest Classifier...")
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=15,
        min_samples_split=10,
        min_samples_leaf=5,
        class_weight=class_weight_dict,
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    return model


def evaluate_model(model, X_test, y_test):
    """Evaluate the trained model."""
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    
    print("\n" + "=" * 60)
    print("MODEL PERFORMANCE METRICS")
    print("=" * 60)
    print(f"ROC-AUC Score: {roc_auc_score(y_test, y_pred_proba):.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=['No Stroke', 'Stroke']))
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred))
    
    return y_pred_proba


def print_feature_importance(model, feature_names):
    """Print the top feature importances."""
    print("\n" + "=" * 60)
    print("TOP 5 MOST IMPORTANT FEATURES")
    print("=" * 60)
    
    feature_importance = pd.DataFrame({
        'feature': feature_names,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    for idx, row in feature_importance.head(5).iterrows():
        print(f"{row['feature']}: {row['importance']:.4f}")


def save_model(model, scaler, le_dict):
    """Save the trained model and preprocessing objects."""
    # Create ml_models directory if it doesn't exist
    os.makedirs('ml_models', exist_ok=True)
    
    pickle.dump(model, open(MODEL_PATH, 'wb'))
    pickle.dump(scaler, open(SCALER_PATH, 'wb'))
    pickle.dump(le_dict, open(ENCODERS_PATH, 'wb'))
    
    print(f"\n✓ Model saved to {MODEL_PATH}")
    print(f"✓ Scaler saved to {SCALER_PATH}")
    print(f"✓ Encoders saved to {ENCODERS_PATH}")


def main():
    """Main training pipeline."""
    # Check if data file exists
    if not os.path.exists(DATA_PATH):
        print(f"Error: Data file not found at {DATA_PATH}")
        print("Please ensure the dataset is in the data/ folder.")
        sys.exit(1)
    
    # Load and preprocess data
    df = load_and_preprocess_data(DATA_PATH)
    
    # Encode categorical variables
    df, le_dict = encode_categorical(df)
    
    # Prepare features and target
    X = df.drop(['id', 'stroke'], axis=1)
    y = df['stroke']
    
    # Split data (80-20)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train model
    model = train_model(X_train_scaled, y_train)
    
    # Evaluate model
    evaluate_model(model, X_test_scaled, y_test)
    
    # Print feature importance
    print_feature_importance(model, X.columns)
    
    # Risk stratification on all data
    all_predictions = model.predict_proba(scaler.transform(X))[:, 1]
    
    low_risk = (all_predictions < 0.33).sum()
    medium_risk = ((all_predictions >= 0.33) & (all_predictions < 0.66)).sum()
    high_risk = (all_predictions >= 0.66).sum()
    
    print("\n" + "=" * 60)
    print("PATIENT RISK STRATIFICATION")
    print("=" * 60)
    print(f"Low Risk (0-33%):     {low_risk} patients ({low_risk/len(df)*100:.1f}%)")
    print(f"Medium Risk (33-66%): {medium_risk} patients ({medium_risk/len(df)*100:.1f}%)")
    print(f"High Risk (66-100%):  {high_risk} patients ({high_risk/len(df)*100:.1f}%)")
    
    # Save model
    save_model(model, scaler, le_dict)
    
    print("\n✓ Training complete!")


if __name__ == '__main__':
    main()

