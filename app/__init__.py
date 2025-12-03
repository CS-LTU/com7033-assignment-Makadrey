"""
Stroke Prediction Application Factory
======================================

This module implements the Application Factory pattern for creating Flask
application instances. The factory pattern provides several benefits:

1. **Testing**: Create app instances with different configurations for testing
2. **Multiple Instances**: Run multiple app instances with different configs
3. **Delayed Configuration**: Configure the app after import time

Architecture Overview:
    - Uses Flask Blueprints for modular route organization
    - Implements Flask-Login for user session management
    - Connects to SQLite (users) and MongoDB (patients) databases
    - Integrates ML model for stroke risk prediction

Example Usage:
    >>> from app import create_app
    >>> from app.config import DevelopmentConfig
    >>> app = create_app(DevelopmentConfig)
    >>> app.run(debug=True)

Author: Healthcare Data Management System
Version: 2.0.0
License: MIT
"""

from flask import Flask
from app.config import Config
from app.extensions import login_manager


def create_app(config_class=Config):
    """
    Application factory function - creates and configures Flask app instance.
    
    This function follows the Factory Pattern, allowing the creation of
    multiple app instances with different configurations. It performs:
    
    1. Flask app initialization with template/static folder setup
    2. Configuration loading from the provided config class
    3. Extension initialization (Flask-Login, etc.)
    4. Blueprint registration for modular routes
    5. Error handler registration (404, 403, 500)
    6. Database initialization (SQLite + MongoDB)
    
    Args:
        config_class (class): Configuration class to use. Defaults to Config.
            Options: Config, DevelopmentConfig, ProductionConfig, TestingConfig
    
    Returns:
        Flask: Fully configured Flask application instance ready to run
    
    Example:
        >>> app = create_app(ProductionConfig)
        >>> app.run(host='0.0.0.0', port=5000)
    
    Note:
        Database initialization happens within app context to ensure
        proper Flask-SQLAlchemy and MongoDB connections.
    """
    # Create Flask application instance
    # __name__ helps Flask locate templates and static files
    app = Flask(__name__)
    
    # Load configuration from the config class
    # This sets SECRET_KEY, database URIs, and other settings
    app.config.from_object(config_class)
    
    # Initialize Flask extensions (Flask-Login, etc.)
    # Extensions are created in extensions.py to avoid circular imports
    _init_extensions(app)
    
    # Register all route blueprints
    # Each blueprint handles a specific feature area (auth, patients, etc.)
    _register_blueprints(app)
    
    # Register custom error handlers for HTTP errors
    # Provides user-friendly error pages instead of default Flask errors
    _register_error_handlers(app)
    
    # Initialize databases within application context
    # App context is required for database operations
    with app.app_context():
        _init_databases()
    
    return app


def _init_extensions(app):
    """
    Initialize Flask extensions with the application instance.
    
    Extensions are instantiated in extensions.py without an app,
    then bound to the app here. This pattern prevents circular imports
    and allows extensions to be used across multiple app instances.
    
    Currently initialized extensions:
        - Flask-Login: User session and authentication management
    
    Args:
        app (Flask): Flask application instance to bind extensions to
    """
    # Bind Flask-Login to the app
    # This enables @login_required decorator and current_user proxy
    login_manager.init_app(app)


def _register_blueprints(app):
    """
    Register all application blueprints with the Flask app.
    
    Blueprints provide modular organization of routes. Each blueprint
    handles a specific feature area:
    
    Blueprints registered:
        - auth_bp: Authentication routes (login, logout, register)
        - dashboard_bp: Main dashboard with statistics
        - patients_bp: Patient CRUD operations
        - analytics_bp: Data visualization and reports
        - prediction_bp: ML stroke risk prediction
        - admin_bp: Admin-only user management
    
    Args:
        app (Flask): Flask application instance
    
    Note:
        Imports are done inside the function to avoid circular imports.
        Blueprints may import from app modules that need the app to exist.
    """
    # Import blueprints inside function to avoid circular imports
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.patients import patients_bp
    from app.routes.analytics import analytics_bp
    from app.routes.prediction import prediction_bp
    from app.routes.admin import admin_bp
    
    # Register each blueprint with the app
    # URL prefixes are defined in individual blueprint files
    app.register_blueprint(auth_bp)          # Routes: /, /login, /logout, /register
    app.register_blueprint(dashboard_bp)      # Routes: /dashboard
    app.register_blueprint(patients_bp)       # Routes: /patients, /patient/*
    app.register_blueprint(analytics_bp)      # Routes: /analytics
    app.register_blueprint(prediction_bp)     # Routes: /predict, /predict-page
    app.register_blueprint(admin_bp)          # Routes: /admin/*


def _register_error_handlers(app):
    """
    Register custom HTTP error handlers.
    
    Provides user-friendly error pages instead of Flask's default
    error responses. Each handler renders a template and returns
    the appropriate HTTP status code.
    
    Handlers registered:
        - 404 Not Found: Page doesn't exist
        - 403 Forbidden: Access denied (authorization failure)
        - 500 Internal Server Error: Unhandled exception
    
    Args:
        app (Flask): Flask application instance
    """
    from flask import render_template
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 Not Found errors."""
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(403)
    def forbidden(error):
        """Handle 403 Forbidden errors (access denied)."""
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 Internal Server errors."""
        return render_template('errors/500.html'), 500


def _init_databases():
    """
    Initialize database connections and schemas on app startup.
    
    This function sets up both database systems used by the application:
    
    1. SQLite (users.db):
        - Stores user authentication data
        - Creates users table if not exists
        - Seeds default admin user if no users exist
    
    2. MongoDB (stroke_prediction):
        - Stores patient medical records
        - Creates indexes for efficient querying
        - Loads initial data from CSV if collection is empty
    
    Note:
        Must be called within Flask application context to access
        configuration values and establish proper connections.
    
    Raises:
        Various database exceptions if connection fails (handled gracefully)
    """
    # Import database initialization functions
    from app.database.sqlite_db import init_sqlite_db
    from app.database.mongo_db import init_mongodb
    
    # Initialize SQLite database for user authentication
    # Creates tables and default admin user if needed
    init_sqlite_db()
    
    # Initialize MongoDB for patient records
    # Creates indexes and loads initial data if needed
    init_mongodb()
