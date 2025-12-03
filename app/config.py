"""
Application Configuration Module
================================

Centralized configuration management for all application environments.
Implements the Configuration Class pattern for Flask applications.

Configuration Hierarchy:
    Config (Base) <-- DevelopmentConfig
                 <-- ProductionConfig
                 <-- TestingConfig

Environment Variables:
    The following environment variables can override defaults:
    
    - SECRET_KEY: Flask secret key for session signing
    - SQLITE_DB_PATH: Path to SQLite database file
    - MONGODB_URI: MongoDB connection string
    - MONGODB_DB: MongoDB database name
    - MODEL_PATH: Path to trained ML model
    - SCALER_PATH: Path to feature scaler
    - ENCODERS_PATH: Path to label encoders
    - DATASET_PATH: Path to stroke dataset CSV
    - LOG_FILE: Path to log file
    - LOG_LEVEL: Logging level (DEBUG, INFO, WARNING, ERROR)

Usage:
    >>> from app.config import DevelopmentConfig
    >>> app.config.from_object(DevelopmentConfig)

Security Notes:
    - Never commit SECRET_KEY to version control
    - Use environment variables for sensitive data in production
    - Enable SESSION_COOKIE_SECURE in production (requires HTTPS)

Author: Healthcare Data Management System
Version: 2.0.0
"""

import os
from datetime import timedelta


class Config:
    """
    Base configuration class with default settings.
    
    All other configuration classes inherit from this class.
    Default values are suitable for development but should be
    overridden for production deployment.
    
    Attributes:
        SECRET_KEY (str): Secret key for signing sessions and tokens.
            CRITICAL: Change this in production!
        
        SESSION_COOKIE_* : Session security settings
        WTF_CSRF_* : Cross-Site Request Forgery protection settings
        SQLITE_DB_PATH (str): Path to SQLite user database
        MONGODB_* : MongoDB connection settings
        MODEL_PATH, SCALER_PATH, ENCODERS_PATH: ML model file paths
        DATASET_PATH (str): Path to training/seed data CSV
        LOG_* : Logging configuration
    """
    
    # ==========================================================================
    # SECURITY CONFIGURATION
    # ==========================================================================
    
    # Secret key for session signing, CSRF tokens, etc.
    # WARNING: Change this to a strong random value in production!
    # Generate with: python -c "import secrets; print(secrets.token_hex(32))"
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # ==========================================================================
    # SESSION COOKIE CONFIGURATION
    # ==========================================================================
    
    # Only send cookie over HTTPS (set True in production)
    SESSION_COOKIE_SECURE = False
    
    # Prevent JavaScript access to session cookie (XSS protection)
    SESSION_COOKIE_HTTPONLY = True
    
    # CSRF protection for cookies
    # 'Strict': Cookie only sent in first-party context
    # 'Lax': Cookie sent with top-level navigations (recommended)
    # 'None': Cookie sent in all contexts (requires Secure=True)
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Session lifetime - user must re-login after this duration
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    
    # ==========================================================================
    # CSRF PROTECTION CONFIGURATION
    # ==========================================================================
    
    # Enable CSRF protection via Flask-WTF
    WTF_CSRF_ENABLED = True
    
    # CSRF token expiration time (None = no expiration within session)
    WTF_CSRF_TIME_LIMIT = None
    
    # ==========================================================================
    # DATABASE CONFIGURATION
    # ==========================================================================
    
    # SQLite Database - stores user authentication data
    # Uses file-based SQLite for simplicity; can be replaced with PostgreSQL
    SQLITE_DB_PATH = os.environ.get('SQLITE_DB_PATH') or 'users.db'
    
    # MongoDB - stores patient medical records
    # Connection URI format: mongodb://[username:password@]host:port/
    MONGODB_URI = os.environ.get('MONGODB_URI') or 'mongodb://localhost:27017/'
    
    # MongoDB database name for patient records
    MONGODB_DB = os.environ.get('MONGODB_DB') or 'stroke_prediction'
    
    # ==========================================================================
    # MACHINE LEARNING MODEL PATHS
    # ==========================================================================
    
    # Trained Random Forest model for stroke prediction
    MODEL_PATH = os.environ.get('MODEL_PATH') or 'ml_models/stroke_model.pkl'
    
    # StandardScaler for feature normalization
    SCALER_PATH = os.environ.get('SCALER_PATH') or 'ml_models/scaler.pkl'
    
    # LabelEncoders for categorical variable encoding
    ENCODERS_PATH = os.environ.get('ENCODERS_PATH') or 'ml_models/label_encoders.pkl'
    
    # ==========================================================================
    # DATA FILES
    # ==========================================================================
    
    # Healthcare stroke dataset for initial data seeding
    DATASET_PATH = os.environ.get('DATASET_PATH') or 'data/healthcare-dataset-stroke-data.csv'
    
    # ==========================================================================
    # LOGGING CONFIGURATION
    # ==========================================================================
    
    # Log file path for security and application events
    LOG_FILE = os.environ.get('LOG_FILE') or 'logs/security.log'
    
    # Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'


class DevelopmentConfig(Config):
    """
    Development environment configuration.
    
    Enables debug mode for detailed error pages and auto-reloading.
    Uses default database paths suitable for local development.
    
    Usage:
        >>> app = create_app(DevelopmentConfig)
    
    Features:
        - Debug mode enabled (detailed error pages)
        - Auto-reload on code changes
        - Development database (users.db)
    """
    
    # Enable Flask debug mode
    # Shows detailed error pages with interactive debugger
    # WARNING: Never enable in production (security risk)
    DEBUG = True
    
    # Not in testing mode
    TESTING = False


class ProductionConfig(Config):
    """
    Production environment configuration.
    
    Disables debug mode and enforces strict security settings.
    Requires environment variables for sensitive configuration.
    
    Usage:
        Set environment variables before starting:
        $ export SECRET_KEY="your-secure-random-key"
        $ export MONGODB_URI="mongodb://user:pass@host:port/"
        $ python run.py
    
    Security Features:
        - Debug mode disabled
        - Secure session cookies (HTTPS required)
        - Secret key must be set via environment variable
    """
    
    # Disable debug mode in production
    DEBUG = False
    TESTING = False
    
    # Require HTTPS for session cookies
    # Prevents session hijacking over unencrypted connections
    SESSION_COOKIE_SECURE = True
    
    # Secret key MUST be set via environment variable in production
    # Application should fail to start if not set
    SECRET_KEY = os.environ.get('SECRET_KEY')


class TestingConfig(Config):
    """
    Testing environment configuration.
    
    Optimized for running automated tests with pytest or unittest.
    Uses in-memory database and disables CSRF for easier testing.
    
    Usage:
        >>> app = create_app(TestingConfig)
        >>> client = app.test_client()
        >>> response = client.get('/login')
    
    Features:
        - In-memory SQLite database (fast, isolated tests)
        - CSRF protection disabled (simplifies form testing)
        - Debug mode enabled for detailed error messages
    """
    
    # Enable debug for detailed test failure messages
    DEBUG = True
    
    # Enable testing mode (changes error handling behavior)
    TESTING = True
    
    # Disable CSRF for testing (allows form posts without tokens)
    WTF_CSRF_ENABLED = False
    
    # Use in-memory SQLite database
    # Each test gets a fresh database; no cleanup needed
    SQLITE_DB_PATH = ':memory:'


# =============================================================================
# CONFIGURATION REGISTRY
# =============================================================================

# Dictionary mapping environment names to configuration classes
# Used by run.py to select configuration based on FLASK_ENV
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig  # Fallback if FLASK_ENV not set
}
