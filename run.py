#!/usr/bin/env python
"""
Stroke Prediction Application Entry Point
==========================================

This is the main entry point for running the Flask application.
It uses the application factory pattern to create and configure
the Flask app instance based on the environment.

Usage:
    Development:
        $ python run.py
        
    Production (with Gunicorn):
        $ gunicorn -w 4 -b 0.0.0.0:5000 "run:app"
    
    With Environment Variables:
        $ export FLASK_ENV=production
        $ export SECRET_KEY="your-secure-key"
        $ python run.py

Environment Variables:
    FLASK_ENV: Environment name ('development', 'production', 'testing')
               Defaults to 'development' if not set
    
    SECRET_KEY: Secret key for session signing (required in production)
    
    MONGODB_URI: MongoDB connection string
                 Default: 'mongodb://localhost:27017/'
    
    See app/config.py for full list of configuration options.

File Structure:
    run.py                 <- You are here (entry point)
    app/
        __init__.py        <- Application factory
        config.py          <- Configuration classes
        extensions.py      <- Flask extensions
        routes/            <- Route blueprints
        services/          <- Business logic
        models/            <- Data models
        database/          <- Database operations
        templates/         <- Jinja2 templates
        static/            <- CSS, JavaScript, images

Default Credentials:
    Username: admin
    Password: admin123
    WARNING: Change these immediately after first login!

Author: Healthcare Data Management System
Version: 2.0.0
License: MIT
"""

import os
import logging

# Import application factory and configuration
from app import create_app
from app.config import config


# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================

# Create logs directory if it doesn't exist
# This ensures the application can write log files on first run
os.makedirs('logs', exist_ok=True)

# Configure basic logging for the application
# Logs are written to both file and console
logging.basicConfig(
    # Log file path
    filename='logs/app.log',
    
    # Minimum log level to record
    # DEBUG < INFO < WARNING < ERROR < CRITICAL
    level=logging.INFO,
    
    # Log message format
    # Example: "2025-01-15 10:30:45,123 - INFO - User logged in: admin"
    format='%(asctime)s - %(levelname)s - %(message)s'
)


# =============================================================================
# APPLICATION CREATION
# =============================================================================

# Determine environment from FLASK_ENV variable
# Options: 'development', 'production', 'testing'
# Default: 'development'
env = os.environ.get('FLASK_ENV', 'development')

# Get the corresponding configuration class
# Falls back to DevelopmentConfig if environment not recognized
config_class = config.get(env, config['default'])

# Create the Flask application using the factory pattern
# This initializes all extensions, blueprints, and databases
app = create_app(config_class)


# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == '__main__':
    """
    Run the Flask development server.
    
    This block only executes when running the script directly:
        $ python run.py
    
    It does NOT execute when imported by a WSGI server:
        $ gunicorn "run:app"
    
    Development Server Features:
        - Auto-reload on code changes (when debug=True)
        - Interactive debugger for errors (when debug=True)
        - Single-threaded (not for production)
    
    Production Deployment:
        Use a production WSGI server like Gunicorn or uWSGI:
        $ gunicorn -w 4 -b 0.0.0.0:5000 "run:app"
    """
    
    # Print startup information
    print("=" * 60)
    print("STROKE PREDICTION MANAGEMENT SYSTEM")
    print("=" * 60)
    print(f"Environment: {env}")
    print(f"Debug Mode: {config_class.DEBUG if hasattr(config_class, 'DEBUG') else 'N/A'}")
    print(f"Access URL: http://127.0.0.1:5000")
    print("=" * 60)
    print("Default Login: admin / admin123")
    print("WARNING: Change default password after first login!")
    print("=" * 60)
    
    # Run the Flask development server
    app.run(
        # Listen on all network interfaces
        # '0.0.0.0' allows access from other devices on the network
        # '127.0.0.1' would only allow local access
        host='0.0.0.0',
        
        # Port to listen on
        # Default Flask port is 5000
        port=5000,
        
        # Debug mode based on environment
        # Development: True (auto-reload, debugger)
        # Production: False (no debugger, no auto-reload)
        debug=(env == 'development')
    )
