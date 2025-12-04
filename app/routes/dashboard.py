"""
Dashboard Routes
================

Main dashboard showing statistics and recent records.
"""

from flask import Blueprint, render_template, flash
from flask_login import login_required

from app.services.patient_service import PatientService


dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/dashboard')
@login_required
def index():
    """
    Main dashboard showing patient statistics and recent records.
    """
    stats = PatientService.get_dashboard_stats()
    
    if stats is None:
        flash('Database connection unavailable. Please contact administrator.', 'danger')
        return render_template('dashboard/index.html', mongo_available=False)
    
    recent_patients = PatientService.get_recent_patients(limit=10)
    
    return render_template(
        'dashboard/index.html',
        stats=stats,
        recent_patients=recent_patients,
        mongo_available=True
    )

