"""
Patient Service
===============

Business logic for patient record operations.
"""

import logging
from datetime import datetime
from app.database.mongo_db import get_patients_collection


class PatientService:
    """Service class for patient operations."""
    
    @staticmethod
    def get_dashboard_stats():
        """
        Get statistics for dashboard.
        
        Returns:
            dict: Dashboard statistics or None if database unavailable
        """
        collection = get_patients_collection()
        if collection is None:
            return None
        
        try:
            total_patients = collection.count_documents({})
            stroke_cases = collection.count_documents({'stroke': 1})
            
            avg_age_result = list(collection.aggregate([
                {'$group': {'_id': None, 'avg_age': {'$avg': '$age'}}}
            ]))
            
            return {
                'total_patients': total_patients,
                'stroke_cases': stroke_cases,
                'no_stroke_cases': total_patients - stroke_cases,
                'avg_age': round(avg_age_result[0]['avg_age'], 1) if avg_age_result else 0
            }
        except Exception as e:
            logging.error(f"Error getting dashboard stats: {e}")
            return None
    
    @staticmethod
    def get_recent_patients(limit=10):
        """
        Get most recent patient records.
        
        Args:
            limit (int): Number of records to return
            
        Returns:
            list: List of patient records
        """
        collection = get_patients_collection()
        if collection is None:
            return []
        
        try:
            return list(collection.find().sort('_id', -1).limit(limit))
        except Exception as e:
            logging.error(f"Error getting recent patients: {e}")
            return []
    
    @staticmethod
    def search_patients(query=None, stroke_filter=None, gender_filter=None, page=1, per_page=20):
        """
        Search and filter patients.
        
        Args:
            query (str): Search query
            stroke_filter (str): Filter by stroke status
            gender_filter (str): Filter by gender
            page (int): Page number
            per_page (int): Records per page
            
        Returns:
            tuple: (patients list, total count, total pages)
        """
        collection = get_patients_collection()
        if collection is None:
            return [], 0, 0
        
        try:
            # Build query
            mongo_query = {}
            
            if query:
                try:
                    patient_id = int(query)
                    mongo_query['id'] = patient_id
                except ValueError:
                    mongo_query['$or'] = [
                        {'gender': {'$regex': query, '$options': 'i'}},
                        {'work_type': {'$regex': query, '$options': 'i'}},
                        {'smoking_status': {'$regex': query, '$options': 'i'}}
                    ]
            
            if stroke_filter:
                mongo_query['stroke'] = int(stroke_filter)
            
            if gender_filter:
                mongo_query['gender'] = gender_filter
            
            # Pagination
            skip = (page - 1) * per_page
            
            patients = list(collection.find(mongo_query).skip(skip).limit(per_page))
            total_count = collection.count_documents(mongo_query)
            total_pages = (total_count + per_page - 1) // per_page
            
            return patients, total_count, total_pages
            
        except Exception as e:
            logging.error(f"Error searching patients: {e}")
            return [], 0, 0
    
    @staticmethod
    def get_patient_by_id(patient_id):
        """
        Get patient by ID.
        
        Args:
            patient_id (int): Patient ID
            
        Returns:
            dict: Patient record or None
        """
        collection = get_patients_collection()
        if collection is None:
            return None
        
        return collection.find_one({'id': patient_id})
    
    @staticmethod
    def create_patient(patient_data, created_by):
        """
        Create new patient record.
        
        Args:
            patient_data (dict): Patient data
            created_by (str): Username of creator
            
        Returns:
            tuple: (success: bool, message: str)
        """
        collection = get_patients_collection()
        if collection is None:
            return False, 'Database connection unavailable.'
        
        try:
            # Check if ID exists
            if collection.find_one({'id': patient_data['id']}):
                return False, 'Patient ID already exists.'
            
            # Add metadata
            patient_data['created_at'] = datetime.now()
            patient_data['updated_at'] = datetime.now()
            patient_data['created_by'] = created_by
            
            collection.insert_one(patient_data)
            logging.info(f"New patient added by {created_by}: ID {patient_data['id']}")
            return True, 'Patient record added successfully!'
            
        except Exception as e:
            logging.error(f"Error creating patient: {e}")
            return False, f'Error adding patient: {str(e)}'
    
    @staticmethod
    def update_patient(patient_id, update_data, updated_by):
        """
        Update patient record.
        
        Args:
            patient_id (int): Patient ID
            update_data (dict): Data to update
            updated_by (str): Username of updater
            
        Returns:
            tuple: (success: bool, message: str)
        """
        collection = get_patients_collection()
        if collection is None:
            return False, 'Database connection unavailable.'
        
        try:
            update_data['updated_at'] = datetime.now()
            update_data['updated_by'] = updated_by
            
            result = collection.update_one({'id': patient_id}, {'$set': update_data})
            
            if result.modified_count > 0:
                logging.info(f"Patient updated by {updated_by}: ID {patient_id}")
                return True, 'Patient record updated successfully!'
            
            return False, 'Patient not found.'
            
        except Exception as e:
            logging.error(f"Error updating patient: {e}")
            return False, f'Error updating patient: {str(e)}'
    
    @staticmethod
    def delete_patient(patient_id, deleted_by):
        """
        Delete patient record.
        
        Args:
            patient_id (int): Patient ID
            deleted_by (str): Username of deleter
            
        Returns:
            tuple: (success: bool, message: str)
        """
        collection = get_patients_collection()
        if collection is None:
            return False, 'Database connection unavailable.'
        
        try:
            result = collection.delete_one({'id': patient_id})
            
            if result.deleted_count > 0:
                logging.info(f"Patient deleted by {deleted_by}: ID {patient_id}")
                return True, 'Patient record deleted successfully.'
            
            return False, 'Patient not found.'
            
        except Exception as e:
            logging.error(f"Error deleting patient: {e}")
            return False, 'Error deleting patient.'
    
    @staticmethod
    def get_analytics_data():
        """
        Get data for analytics dashboard.
        
        Returns:
            dict: Analytics data or None
        """
        collection = get_patients_collection()
        if collection is None:
            return None
        
        try:
            # Gender distribution
            gender_dist = list(collection.aggregate([
                {'$group': {'_id': '$gender', 'count': {'$sum': 1}}}
            ]))
            
            # Stroke by age group
            age_groups = list(collection.aggregate([
                {'$bucket': {
                    'groupBy': '$age',
                    'boundaries': [0, 20, 40, 60, 80, 120],
                    'default': 'Other',
                    'output': {
                        'count': {'$sum': 1},
                        'stroke_count': {'$sum': '$stroke'}
                    }
                }}
            ]))
            
            # Health correlation
            health_correlation = list(collection.aggregate([
                {'$group': {
                    '_id': {
                        'hypertension': '$hypertension',
                        'heart_disease': '$heart_disease'
                    },
                    'count': {'$sum': 1},
                    'stroke_count': {'$sum': '$stroke'}
                }}
            ]))
            
            # Smoking and stroke
            smoking_stroke = list(collection.aggregate([
                {'$group': {
                    '_id': '$smoking_status',
                    'count': {'$sum': 1},
                    'stroke_count': {'$sum': '$stroke'}
                }}
            ]))
            
            return {
                'gender_dist': gender_dist,
                'age_groups': age_groups,
                'health_correlation': health_correlation,
                'smoking_stroke': smoking_stroke
            }
            
        except Exception as e:
            logging.error(f"Error getting analytics data: {e}")
            return None

