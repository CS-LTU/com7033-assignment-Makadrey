"""
Routes Module
=============

Blueprint registration for all application routes.
"""

from app.routes.auth import auth_bp
from app.routes.dashboard import dashboard_bp
from app.routes.patients import patients_bp
from app.routes.analytics import analytics_bp
from app.routes.prediction import prediction_bp
from app.routes.admin import admin_bp

__all__ = [
    'auth_bp',
    'dashboard_bp',
    'patients_bp',
    'analytics_bp',
    'prediction_bp',
    'admin_bp'
]

