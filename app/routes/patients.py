"""
Patient Routes
==============

CRUD operations for patient records.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from app.services.patient_service import PatientService
from app.utils.validators import sanitize_input, validate_patient_data


patients_bp = Blueprint('patients', __name__)


@patients_bp.route('/patients')
@login_required
def list_patients():
    """
    Display all patients with search and filter capabilities.
    """
    # Get search and filter parameters
    search_query = request.args.get('search', '')
    stroke_filter = request.args.get('stroke_filter', '')
    gender_filter = request.args.get('gender_filter', '')
    page = int(request.args.get('page', 1))
    
    if search_query:
        search_query = sanitize_input(search_query)
    
    patients, total_count, total_pages = PatientService.search_patients(
        query=search_query or None,
        stroke_filter=stroke_filter or None,
        gender_filter=gender_filter or None,
        page=page
    )
    
    if patients is None:
        flash('Database connection unavailable.', 'danger')
        return render_template('patients/list.html', patients=[], mongo_available=False)
    
    return render_template(
        'patients/list.html',
        patients=patients,
        page=page,
        total_pages=total_pages,
        search_query=search_query,
        stroke_filter=stroke_filter,
        gender_filter=gender_filter,
        mongo_available=True
    )


@patients_bp.route('/patient/<int:patient_id>')
@login_required
def view_patient(patient_id):
    """
    View detailed patient information.
    """
    patient = PatientService.get_patient_by_id(patient_id)
    
    if patient is None:
        flash('Patient not found.', 'danger')
        return redirect(url_for('patients.list_patients'))
    
    return render_template('patients/view.html', patient=patient)


@patients_bp.route('/patient/add', methods=['GET', 'POST'])
@login_required
def add_patient():
    """
    Add new patient record.
    """
    if request.method == 'POST':
        try:
            patient_data = {
                'id': int(request.form.get('patient_id')),
                'gender': sanitize_input(request.form.get('gender')),
                'age': float(request.form.get('age')),
                'hypertension': int(request.form.get('hypertension')),
                'heart_disease': int(request.form.get('heart_disease')),
                'ever_married': sanitize_input(request.form.get('ever_married')),
                'work_type': sanitize_input(request.form.get('work_type')),
                'Residence_type': sanitize_input(request.form.get('Residence_type')),
                'avg_glucose_level': float(request.form.get('avg_glucose_level')),
                'smoking_status': sanitize_input(request.form.get('smoking_status')),
                'stroke': int(request.form.get('stroke'))
            }
            
            # Handle BMI
            bmi = request.form.get('bmi')
            if bmi and bmi != 'N/A':
                patient_data['bmi'] = float(bmi)
            else:
                patient_data['bmi'] = 'N/A'
            
            # Validate data
            is_valid, error_msg = validate_patient_data(patient_data)
            if not is_valid:
                flash(error_msg, 'danger')
                return render_template('patients/add.html')
            
            # Create patient
            success, message = PatientService.create_patient(
                patient_data, 
                current_user.username
            )
            
            if success:
                flash(message, 'success')
                return redirect(url_for('patients.list_patients'))
            else:
                flash(message, 'danger')
                
        except Exception as e:
            flash(f'Error adding patient: {str(e)}', 'danger')
    
    return render_template('patients/add.html')


@patients_bp.route('/patient/edit/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def edit_patient(patient_id):
    """
    Edit existing patient record.
    """
    patient = PatientService.get_patient_by_id(patient_id)
    
    if patient is None:
        flash('Patient not found.', 'danger')
        return redirect(url_for('patients.list_patients'))
    
    if request.method == 'POST':
        try:
            update_data = {
                'gender': sanitize_input(request.form.get('gender')),
                'age': float(request.form.get('age')),
                'hypertension': int(request.form.get('hypertension')),
                'heart_disease': int(request.form.get('heart_disease')),
                'ever_married': sanitize_input(request.form.get('ever_married')),
                'work_type': sanitize_input(request.form.get('work_type')),
                'Residence_type': sanitize_input(request.form.get('Residence_type')),
                'avg_glucose_level': float(request.form.get('avg_glucose_level')),
                'smoking_status': sanitize_input(request.form.get('smoking_status')),
                'stroke': int(request.form.get('stroke'))
            }
            
            # Handle BMI
            bmi = request.form.get('bmi')
            if bmi and bmi != 'N/A':
                update_data['bmi'] = float(bmi)
            else:
                update_data['bmi'] = 'N/A'
            
            # Validate data
            is_valid, error_msg = validate_patient_data(update_data)
            if not is_valid:
                flash(error_msg, 'danger')
                return render_template('patients/edit.html', patient=patient)
            
            # Update patient
            success, message = PatientService.update_patient(
                patient_id,
                update_data,
                current_user.username
            )
            
            if success:
                flash(message, 'success')
                return redirect(url_for('patients.list_patients'))
            else:
                flash(message, 'danger')
                
        except Exception as e:
            flash(f'Error updating patient: {str(e)}', 'danger')
    
    return render_template('patients/edit.html', patient=patient)


@patients_bp.route('/patient/delete/<int:patient_id>', methods=['POST'])
@login_required
def delete_patient(patient_id):
    """
    Delete patient record.
    """
    success, message = PatientService.delete_patient(
        patient_id,
        current_user.username
    )
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    
    return redirect(url_for('patients.list_patients'))

