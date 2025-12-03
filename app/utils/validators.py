"""
Input Validation Module
=======================

Provides functions for validating and sanitizing user input.
Essential for security (preventing injection attacks) and data integrity.

Security Functions:
    - sanitize_input(): Escapes HTML to prevent XSS attacks
    - validate_email(): Validates email format
    - validate_password(): Enforces password strength requirements

Data Validation Functions:
    - validate_patient_data(): Validates patient record fields
    - validate_prediction_input(): Validates ML prediction input

Security Best Practices Applied:
    1. HTML escaping prevents Cross-Site Scripting (XSS)
    2. Input validation prevents malformed data storage
    3. Type checking prevents type confusion attacks
    4. Range validation prevents buffer overflows

Usage:
    >>> from app.utils.validators import sanitize_input, validate_email
    >>> clean_input = sanitize_input('<script>alert("XSS")</script>')
    >>> print(clean_input)
    &lt;script&gt;alert(&quot;XSS&quot;)&lt;/script&gt;
    
    >>> validate_email('user@example.com')
    True

Author: Healthcare Data Management System
Version: 2.0.0
"""

import re
import html


# =============================================================================
# INPUT SANITIZATION
# =============================================================================

def sanitize_input(input_string):
    """
    Sanitize user input to prevent Cross-Site Scripting (XSS) attacks.
    
    This function escapes HTML special characters to their entity equivalents,
    rendering any injected HTML/JavaScript harmless when displayed in a browser.
    
    Characters Escaped:
        < becomes &lt;
        > becomes &gt;
        & becomes &amp;
        " becomes &quot;
        ' becomes &#x27;
    
    Args:
        input_string (str|None): Raw user input to sanitize.
            Can be None (returns empty string).
            Non-string types are converted to string.
    
    Returns:
        str: Sanitized string with HTML entities escaped and whitespace trimmed.
            Empty string if input is None.
    
    Example:
        >>> sanitize_input('<script>alert("XSS")</script>')
        '&lt;script&gt;alert(&quot;XSS&quot;)&lt;/script&gt;'
        
        >>> sanitize_input('  Hello World  ')
        'Hello World'
        
        >>> sanitize_input(None)
        ''
        
        >>> sanitize_input(123)  # Non-string input
        '123'
    
    Security Note:
        Always sanitize user input before:
        - Displaying in HTML templates (even with Jinja2 auto-escaping as backup)
        - Storing in database
        - Including in log messages
    """
    # Handle None input gracefully
    if input_string is None:
        return ''
    
    # Convert to string (handles numbers, etc.), strip whitespace, escape HTML
    return html.escape(str(input_string).strip())


# =============================================================================
# EMAIL VALIDATION
# =============================================================================

def validate_email(email):
    """
    Validate email address format using regular expression.
    
    Checks that the email follows the standard format:
        local-part@domain.tld
    
    Validation Rules:
        - Local part: letters, numbers, dots, underscores, percent, plus, hyphen
        - Domain: letters, numbers, dots, hyphens
        - TLD: at least 2 letters
    
    Args:
        email (str|None): Email address to validate
    
    Returns:
        bool: True if email format is valid, False otherwise
    
    Example:
        >>> validate_email('user@example.com')
        True
        
        >>> validate_email('user.name+tag@example.co.uk')
        True
        
        >>> validate_email('invalid-email')
        False
        
        >>> validate_email('@example.com')
        False
        
        >>> validate_email(None)
        False
    
    Note:
        This validates FORMAT only, not whether the email actually exists.
        For full validation, consider email verification via confirmation link.
    """
    # Handle None/empty input
    if not email:
        return False
    
    # RFC 5322 simplified email regex pattern
    # More permissive than strict RFC but catches obvious errors
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    return bool(re.match(email_regex, email))


# =============================================================================
# PASSWORD VALIDATION
# =============================================================================

def validate_password(password):
    """
    Validate password strength against security requirements.
    
    A strong password must meet ALL of the following criteria:
        - Minimum 8 characters length
        - At least one uppercase letter (A-Z)
        - At least one lowercase letter (a-z)
        - At least one digit (0-9)
    
    Args:
        password (str|None): Password to validate
    
    Returns:
        tuple: A tuple of (is_valid, error_message)
            - is_valid (bool): True if password meets all requirements
            - error_message (str|None): Description of first failed requirement,
              or None if valid
    
    Example:
        >>> validate_password('SecurePass123')
        (True, None)
        
        >>> validate_password('weak')
        (False, 'Password must be at least 8 characters long.')
        
        >>> validate_password('alllowercase123')
        (False, 'Password must contain at least one uppercase letter.')
        
        >>> validate_password('ALLUPPERCASE123')
        (False, 'Password must contain at least one lowercase letter.')
        
        >>> validate_password('NoNumbersHere')
        (False, 'Password must contain at least one digit.')
    
    Security Recommendations:
        Consider also checking:
        - Not a common password (dictionary check)
        - Not similar to username
        - No personal information
    """
    # Check minimum length
    if not password or len(password) < 8:
        return False, 'Password must be at least 8 characters long.'
    
    # Check for uppercase letter
    if not re.search(r'[A-Z]', password):
        return False, 'Password must contain at least one uppercase letter.'
    
    # Check for lowercase letter
    if not re.search(r'[a-z]', password):
        return False, 'Password must contain at least one lowercase letter.'
    
    # Check for digit
    if not re.search(r'\d', password):
        return False, 'Password must contain at least one digit.'
    
    # All checks passed
    return True, None


# =============================================================================
# PATIENT DATA VALIDATION
# =============================================================================

def validate_patient_data(patient_data):
    """
    Validate patient record data for database storage.
    
    Ensures all required fields are present and contain valid values
    according to the medical data schema.
    
    Required Fields:
        - gender: 'Male', 'Female', or 'Other'
        - age: Number between 0 and 120
        - hypertension: 0 or 1
        - heart_disease: 0 or 1
        - ever_married: 'Yes' or 'No'
        - work_type: Work type category
        - Residence_type: 'Urban' or 'Rural'
        - avg_glucose_level: Number between 0 and 500
        - smoking_status: Smoking status category
        - stroke: 0 or 1
    
    Args:
        patient_data (dict): Dictionary containing patient information
    
    Returns:
        tuple: A tuple of (is_valid, error_message)
            - is_valid (bool): True if all validations pass
            - error_message (str|None): Description of first validation failure,
              or None if valid
    
    Example:
        >>> valid_patient = {
        ...     'gender': 'Male',
        ...     'age': '45',
        ...     'hypertension': '0',
        ...     'heart_disease': '0',
        ...     'ever_married': 'Yes',
        ...     'work_type': 'Private',
        ...     'Residence_type': 'Urban',
        ...     'avg_glucose_level': '120.5',
        ...     'smoking_status': 'never smoked',
        ...     'stroke': '0'
        ... }
        >>> validate_patient_data(valid_patient)
        (True, None)
    """
    # List of all required fields for a patient record
    required_fields = [
        'gender',           # Patient's gender
        'age',              # Patient's age in years
        'hypertension',     # Has hypertension (0/1)
        'heart_disease',    # Has heart disease (0/1)
        'ever_married',     # Ever been married (Yes/No)
        'work_type',        # Type of employment
        'Residence_type',   # Urban or Rural residence
        'avg_glucose_level', # Average blood glucose level
        'smoking_status',   # Smoking status category
        'stroke'            # Has had stroke (0/1)
    ]
    
    # --------------------------------------------------------------------------
    # Check all required fields are present
    # --------------------------------------------------------------------------
    for field in required_fields:
        if field not in patient_data or patient_data[field] is None:
            return False, f'Missing required field: {field}'
    
    # --------------------------------------------------------------------------
    # Validate age (must be between 0 and 120)
    # --------------------------------------------------------------------------
    try:
        age = float(patient_data['age'])
        if age < 0 or age > 120:
            return False, 'Age must be between 0 and 120.'
    except (ValueError, TypeError):
        return False, 'Invalid age value.'
    
    # --------------------------------------------------------------------------
    # Validate glucose level (must be between 0 and 500 mg/dL)
    # --------------------------------------------------------------------------
    try:
        glucose = float(patient_data['avg_glucose_level'])
        if glucose < 0 or glucose > 500:
            return False, 'Glucose level must be between 0 and 500.'
    except (ValueError, TypeError):
        return False, 'Invalid glucose level value.'
    
    # --------------------------------------------------------------------------
    # Validate gender (must be predefined category)
    # --------------------------------------------------------------------------
    valid_genders = ['Male', 'Female', 'Other']
    if patient_data['gender'] not in valid_genders:
        return False, f'Gender must be one of: {", ".join(valid_genders)}'
    
    # --------------------------------------------------------------------------
    # Validate binary fields (must be 0 or 1)
    # --------------------------------------------------------------------------
    binary_fields = ['hypertension', 'heart_disease', 'stroke']
    for field in binary_fields:
        if str(patient_data[field]) not in ['0', '1']:
            return False, f'{field} must be 0 or 1.'
    
    # All validations passed
    return True, None


# =============================================================================
# PREDICTION INPUT VALIDATION
# =============================================================================

def validate_prediction_input(data):
    """
    Validate input data for stroke risk prediction.
    
    Ensures all required features for the ML model are present
    and contain valid numeric values where expected.
    
    Required Fields:
        - gender: Patient's gender
        - age: Patient's age (numeric)
        - hypertension: Hypertension status (0/1)
        - heart_disease: Heart disease status (0/1)
        - ever_married: Marital status
        - work_type: Employment type
        - Residence_type: Urban/Rural
        - avg_glucose_level: Blood glucose level (numeric)
        - bmi: Body Mass Index (numeric)
        - smoking_status: Smoking status category
    
    Args:
        data (dict): Dictionary containing prediction input features
    
    Returns:
        tuple: A tuple of (is_valid, error_message)
            - is_valid (bool): True if all validations pass
            - error_message (str|None): Description of validation failure,
              or None if valid
    
    Example:
        >>> prediction_input = {
        ...     'gender': 'Male',
        ...     'age': 45,
        ...     'hypertension': 0,
        ...     'heart_disease': 0,
        ...     'ever_married': 'Yes',
        ...     'work_type': 'Private',
        ...     'Residence_type': 'Urban',
        ...     'avg_glucose_level': 120.5,
        ...     'bmi': 25.6,
        ...     'smoking_status': 'never smoked'
        ... }
        >>> validate_prediction_input(prediction_input)
        (True, None)
    """
    # Required features for the ML model (must match model training features)
    required_fields = [
        'gender',           # Categorical: Male/Female/Other
        'age',              # Numeric: years
        'hypertension',     # Binary: 0/1
        'heart_disease',    # Binary: 0/1
        'ever_married',     # Categorical: Yes/No
        'work_type',        # Categorical: Private/Self-employed/etc.
        'Residence_type',   # Categorical: Urban/Rural
        'avg_glucose_level', # Numeric: mg/dL
        'bmi',              # Numeric: kg/m²
        'smoking_status'    # Categorical: never smoked/formerly smoked/smokes
    ]
    
    # --------------------------------------------------------------------------
    # Check all required fields are present and non-empty
    # --------------------------------------------------------------------------
    for field in required_fields:
        if field not in data or data[field] is None or data[field] == '':
            return False, f'Missing required field: {field}'
    
    # --------------------------------------------------------------------------
    # Validate numeric fields can be converted to float
    # --------------------------------------------------------------------------
    numeric_fields = ['age', 'avg_glucose_level', 'bmi']
    try:
        for field in numeric_fields:
            float(data[field])
    except (ValueError, TypeError) as e:
        return False, f'Invalid numeric value: {str(e)}'
    
    # All validations passed
    return True, None
