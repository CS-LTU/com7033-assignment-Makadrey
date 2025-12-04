"""
Analytics Routes
================

Data visualization and analytics dashboard.
"""

from flask import Blueprint, render_template, flash
from flask_login import login_required

from app.services.patient_service import PatientService


analytics_bp = Blueprint('analytics', __name__)


@analytics_bp.route('/analytics')
@login_required
def index():
    """
    Display analytics and visualizations of patient data.
    """
    data = PatientService.get_analytics_data()
    
    if data is None:
        flash('Database connection unavailable.', 'danger')
        return render_template('analytics/index.html', mongo_available=False)
    
    return render_template(
        'analytics/index.html',
        data=data,
        mongo_available=True
    )

