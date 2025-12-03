"""
MongoDB Database Module
=======================

Handles MongoDB database operations for patient records.

Responsibilities:
- MongoDB connection management
- Patient collection initialization
- Patient CRUD operations
- Data aggregations for analytics
"""

import logging
from datetime import datetime
import pandas as pd
from pymongo import MongoClient
from flask import current_app


# Module-level connection cache
_mongo_client = None
_mongo_db = None


def get_mongo_connection():
    """
    Create and return MongoDB connection for patient records.
    Uses connection pooling for efficiency.
    
    Returns:
        pymongo.database.Database: MongoDB database instance or None if connection fails
    """
    global _mongo_client, _mongo_db
    
    try:
        mongodb_uri = current_app.config.get('MONGODB_URI', 'mongodb://localhost:27017/')
        mongodb_db = current_app.config.get('MONGODB_DB', 'stroke_prediction')
        
        if _mongo_client is None:
            _mongo_client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
            # Test connection
            _mongo_client.server_info()
            logging.info("Connected to MongoDB successfully")
        
        _mongo_db = _mongo_client[mongodb_db]
        return _mongo_db
        
    except Exception as e:
        logging.error(f"MongoDB connection failed: {str(e)}")
        return None


def init_mongodb():
    """
    Initialize MongoDB with patient records collection.
    Loads data from CSV file if collection is empty.
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        db = get_mongo_connection()
        if db is None:
            logging.warning("MongoDB not available - skipping initialization")
            return False
        
        collection = db['patients']
        
        # Create indexes for efficient querying
        collection.create_index('id', unique=True)
        collection.create_index('age')
        collection.create_index('stroke')
        collection.create_index('gender')
        
        # Load CSV data if collection is empty
        if collection.count_documents({}) == 0:
            dataset_path = current_app.config.get('DATASET_PATH', 'data/healthcare-dataset-stroke-data.csv')
            
            # Try multiple possible paths
            possible_paths = [
                dataset_path,
                'healthcare-dataset-stroke-data.csv',
                'data/healthcare-dataset-stroke-data.csv'
            ]
            
            df = None
            for path in possible_paths:
                try:
                    df = pd.read_csv(path)
                    logging.info(f"Loaded dataset from {path}")
                    break
                except FileNotFoundError:
                    continue
            
            if df is None:
                logging.warning("Dataset CSV not found - skipping data load")
                return True
            
            # Clean and prepare data
            df = df.fillna('N/A')
            records = df.to_dict('records')
            
            # Convert numeric fields
            for record in records:
                record['id'] = int(record['id'])
                record['age'] = float(record['age'])
                record['hypertension'] = int(record['hypertension'])
                record['heart_disease'] = int(record['heart_disease'])
                record['stroke'] = int(record['stroke'])
                
                # Handle BMI
                if record['bmi'] != 'N/A':
                    try:
                        record['bmi'] = float(record['bmi'])
                    except (ValueError, TypeError):
                        record['bmi'] = 'N/A'
                
                # Handle glucose level
                if record['avg_glucose_level'] != 'N/A':
                    try:
                        record['avg_glucose_level'] = float(record['avg_glucose_level'])
                    except (ValueError, TypeError):
                        pass
                
                # Add metadata
                record['created_at'] = datetime.now()
                record['updated_at'] = datetime.now()
            
            collection.insert_many(records)
            logging.info(f"Loaded {len(records)} patient records into MongoDB")
        
        return True
        
    except Exception as e:
        logging.error(f"MongoDB initialization failed: {str(e)}")
        return False


def get_patients_collection():
    """
    Get the patients collection.
    
    Returns:
        pymongo.collection.Collection: Patients collection or None
    """
    db = get_mongo_connection()
    if db is None:
        return None
    return db['patients']

