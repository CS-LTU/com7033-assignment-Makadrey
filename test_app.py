"""
Unit Tests for Stroke Prediction Management System
===================================================

This module contains comprehensive unit tests for the Flask application,
covering authentication, database operations, security features, and CRUD operations.

Author: Healthcare Data Management System
License: MIT
"""

import unittest
import os
import sys
import tempfile
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import bcrypt

# Import from new modular structure
from app import create_app
from app.config import TestingConfig
from app.utils.validators import (
    sanitize_input, 
    validate_email, 
    validate_password, 
    validate_patient_data
)


class TestSecurityFunctions(unittest.TestCase):
    """Test suite for security-related functions."""
    
    def test_sanitize_input_removes_dangerous_chars(self):
        """Test that sanitize_input escapes potentially dangerous characters."""
        dangerous_input = "<script>alert('XSS')</script>"
        sanitized = sanitize_input(dangerous_input)
        self.assertNotIn('<script>', sanitized)
        self.assertIn('&lt;', sanitized)  # HTML escaped
    
    def test_sanitize_input_handles_html_entities(self):
        """Test that sanitize_input handles HTML entities."""
        html_input = "<div>Test & Demo</div>"
        sanitized = sanitize_input(html_input)
        self.assertNotIn('<div>', sanitized)
    
    def test_sanitize_input_preserves_safe_strings(self):
        """Test that sanitize_input preserves safe strings."""
        safe_input = "John Doe 123"
        sanitized = sanitize_input(safe_input)
        self.assertEqual(sanitized, "John Doe 123")
    
    def test_sanitize_input_handles_none(self):
        """Test that sanitize_input handles None input."""
        sanitized = sanitize_input(None)
        self.assertEqual(sanitized, '')
    
    def test_validate_email_accepts_valid_emails(self):
        """Test that validate_email accepts valid email addresses."""
        valid_emails = [
            'test@example.com',
            'user.name@domain.co.uk',
            'first+last@test.org'
        ]
        for email in valid_emails:
            self.assertTrue(validate_email(email), f"Should accept {email}")
    
    def test_validate_email_rejects_invalid_emails(self):
        """Test that validate_email rejects invalid email addresses."""
        invalid_emails = [
            'notanemail',
            '@example.com',
            'user@',
            'user @example.com',
            'user@example',
            '',
            None
        ]
        for email in invalid_emails:
            self.assertFalse(validate_email(email), f"Should reject {email}")
    
    def test_validate_password_strength_requirements(self):
        """Test password validation enforces all requirements."""
        # Too short
        is_valid, msg = validate_password('Short1')
        self.assertFalse(is_valid)
        self.assertIn('8 characters', msg)
        
        # No uppercase
        is_valid, msg = validate_password('lowercase123')
        self.assertFalse(is_valid)
        self.assertIn('uppercase', msg)
        
        # No lowercase
        is_valid, msg = validate_password('UPPERCASE123')
        self.assertFalse(is_valid)
        self.assertIn('lowercase', msg)
        
        # No number
        is_valid, msg = validate_password('NoNumbersHere')
        self.assertFalse(is_valid)
        self.assertIn('digit', msg)
        
        # Valid password
        is_valid, msg = validate_password('ValidPass123')
        self.assertTrue(is_valid)
        self.assertIsNone(msg)


class TestPatientDataValidation(unittest.TestCase):
    """Test suite for patient data validation."""
    
    def setUp(self):
        """Set up test data."""
        self.valid_patient = {
            'gender': 'Male',
            'age': '45',
            'hypertension': '0',
            'heart_disease': '1',
            'ever_married': 'Yes',
            'work_type': 'Private',
            'Residence_type': 'Urban',
            'avg_glucose_level': '120.5',
            'bmi': '25.6',
            'smoking_status': 'never smoked',
            'stroke': '0'
        }
    
    def test_validate_patient_accepts_valid_data(self):
        """Test that validate_patient_data accepts valid patient data."""
        is_valid, msg = validate_patient_data(self.valid_patient)
        self.assertTrue(is_valid)
        self.assertIsNone(msg)
    
    def test_validate_patient_rejects_missing_fields(self):
        """Test that validate_patient_data rejects missing required fields."""
        incomplete_patient = self.valid_patient.copy()
        del incomplete_patient['gender']
        
        is_valid, msg = validate_patient_data(incomplete_patient)
        self.assertFalse(is_valid)
        self.assertIn('gender', msg.lower())
    
    def test_validate_patient_rejects_invalid_age(self):
        """Test that validate_patient_data rejects invalid age values."""
        # Negative age
        invalid_patient = self.valid_patient.copy()
        invalid_patient['age'] = '-5'
        is_valid, msg = validate_patient_data(invalid_patient)
        self.assertFalse(is_valid)
        
        # Age too high
        invalid_patient['age'] = '150'
        is_valid, msg = validate_patient_data(invalid_patient)
        self.assertFalse(is_valid)
    
    def test_validate_patient_rejects_invalid_glucose(self):
        """Test that validate_patient_data rejects invalid glucose levels."""
        invalid_patient = self.valid_patient.copy()
        
        # Negative glucose
        invalid_patient['avg_glucose_level'] = '-10'
        is_valid, msg = validate_patient_data(invalid_patient)
        self.assertFalse(is_valid)
        
        # Glucose too high
        invalid_patient['avg_glucose_level'] = '600'
        is_valid, msg = validate_patient_data(invalid_patient)
        self.assertFalse(is_valid)
    
    def test_validate_patient_rejects_invalid_categorical_values(self):
        """Test that validate_patient_data rejects invalid categorical values."""
        invalid_patient = self.valid_patient.copy()
        
        # Invalid gender
        invalid_patient['gender'] = 'Invalid'
        is_valid, msg = validate_patient_data(invalid_patient)
        self.assertFalse(is_valid)
        
        # Invalid hypertension value
        invalid_patient = self.valid_patient.copy()
        invalid_patient['hypertension'] = '2'
        is_valid, msg = validate_patient_data(invalid_patient)
        self.assertFalse(is_valid)


class TestFlaskApplication(unittest.TestCase):
    """Test suite for Flask application routes and functionality."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test Flask application once for all tests."""
        cls.app = create_app(TestingConfig)
        cls.client = cls.app.test_client()
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests."""
        cls.app_context.pop()
    
    def test_index_redirects_to_login(self):
        """Test that index page redirects to login for unauthenticated users."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.location)
    
    def test_login_page_loads(self):
        """Test that login page loads successfully."""
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)
    
    def test_register_page_loads(self):
        """Test that registration page loads successfully."""
        response = self.client.get('/register')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Register', response.data)
    
    def test_dashboard_requires_authentication(self):
        """Test that dashboard requires authentication."""
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.location)
    
    def test_patients_page_requires_authentication(self):
        """Test that patients page requires authentication."""
        response = self.client.get('/patients')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.location)
    
    def test_analytics_requires_authentication(self):
        """Test that analytics page requires authentication."""
        response = self.client.get('/analytics')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.location)
    
    def test_prediction_page_requires_authentication(self):
        """Test that prediction page requires authentication."""
        response = self.client.get('/predict-page')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.location)


class TestPasswordHashing(unittest.TestCase):
    """Test suite for password hashing functionality."""
    
    def test_password_hashing_creates_different_hashes(self):
        """Test that same password creates different hashes each time."""
        password = 'TestPassword123'
        hash1 = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        hash2 = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        self.assertNotEqual(hash1, hash2)
    
    def test_password_verification_works(self):
        """Test that password verification works correctly."""
        password = 'TestPassword123'
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Correct password should verify
        self.assertTrue(bcrypt.checkpw(password.encode('utf-8'), password_hash))
        
        # Incorrect password should not verify
        self.assertFalse(bcrypt.checkpw('WrongPassword'.encode('utf-8'), password_hash))


class TestInputSanitization(unittest.TestCase):
    """Test suite for input sanitization against XSS and injection attacks."""
    
    def test_xss_prevention(self):
        """Test that XSS attempts are sanitized."""
        xss_attempts = [
            '<script>alert("XSS")</script>',
            '<img src=x onerror=alert("XSS")>',
            '<iframe src="javascript:alert(\'XSS\')">',
            '"><script>alert(String.fromCharCode(88,83,83))</script>'
        ]
        
        for xss in xss_attempts:
            sanitized = sanitize_input(xss)
            self.assertNotIn('<script>', sanitized)
            self.assertNotIn('<iframe>', sanitized)
            
    
    def test_html_entities_escaped(self):
        """Test that HTML special characters are escaped."""
        dangerous = '<>&"'
        sanitized = sanitize_input(dangerous)
        self.assertIn('&lt;', sanitized)
        self.assertIn('&gt;', sanitized)
        self.assertIn('&amp;', sanitized)


def run_tests():
    """Run all test suites and generate report."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test cases
    suite.addTests(loader.loadTestsFromTestCase(TestSecurityFunctions))
    suite.addTests(loader.loadTestsFromTestCase(TestPatientDataValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestFlaskApplication))
    suite.addTests(loader.loadTestsFromTestCase(TestPasswordHashing))
    suite.addTests(loader.loadTestsFromTestCase(TestInputSanitization))
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests Run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*70)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    # Run tests
    success = run_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)
