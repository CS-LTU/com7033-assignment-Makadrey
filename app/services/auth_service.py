"""
Authentication Service Module
=============================

Provides business logic for user authentication operations.

This service layer separates authentication logic from route handlers,
following the Single Responsibility Principle. Routes handle HTTP
concerns; services handle business logic.

Services Provided:
    - authenticate(): Verify user credentials and create session
    - register(): Create new user account with password hashing

Security Features:
    - bcrypt password hashing (adaptive, salted)
    - Timing-safe password comparison
    - Failed login attempt logging
    - Successful authentication logging

Architecture:
    Routes -> AuthService -> Database (sqlite_db)
    
    The service layer provides:
    1. Input processing (but not validation - that's in validators.py)
    2. Business rule enforcement
    3. Database coordination
    4. Logging of security events

Usage:
    >>> from app.services.auth_service import AuthService
    >>> user = AuthService.authenticate('admin', 'admin123')
    >>> if user:
    ...     login_user(user)  # Flask-Login

Author: Healthcare Data Management System
Version: 2.0.0
"""

import logging

import bcrypt

from app.database.sqlite_db import (
    get_user_by_username,
    create_user,
    user_exists,
    update_last_login
)
from app.models.user import User


class AuthService:
    """
    Service class for user authentication operations.
    
    This class uses static methods as it doesn't maintain state.
    All methods are self-contained and can be called directly on the class.
    
    Methods:
        authenticate: Verify credentials and return User or None
        register: Create new user account
    
    Example:
        >>> # Authentication
        >>> user = AuthService.authenticate('admin', 'password')
        >>> if user:
        ...     print(f"Welcome, {user.username}!")
        
        >>> # Registration
        >>> success, message = AuthService.register('newuser', 'email@test.com', 'Password123')
        >>> if success:
        ...     print("Registration successful!")
    """
    
    @staticmethod
    def authenticate(username, password):
        """
        Authenticate a user with username and password.
        
        This method:
        1. Retrieves user data from database by username
        2. Verifies password using bcrypt (timing-safe comparison)
        3. Updates last_login timestamp on success
        4. Returns User object or None
        5. Logs authentication attempts (success and failure)
        
        Security Notes:
            - bcrypt.checkpw() is timing-safe (prevents timing attacks)
            - Password is never logged (only username)
            - Both success and failure are logged for security auditing
        
        Args:
            username (str): The username to authenticate.
                Should be pre-sanitized by the route handler.
            
            password (str): The plain-text password to verify.
                NEVER log or store this value.
        
        Returns:
            User: User object if authentication succeeds.
                Contains: id, username, email, is_admin
                Can be passed to Flask-Login's login_user()
            
            None: If authentication fails for any reason:
                - Username not found
                - Password incorrect
                - Database error
        
        Example:
            >>> user = AuthService.authenticate('admin', 'admin123')
            >>> if user:
            ...     login_user(user)  # Flask-Login
            ...     return redirect(url_for('dashboard.index'))
            ... else:
            ...     flash('Invalid credentials', 'danger')
        
        Logging:
            - INFO: "User logged in: {username}" on success
            - WARNING: "Failed login attempt for username: {username}" on failure
        """
        # Retrieve user data from database
        # Returns sqlite3.Row or None
        user_data = get_user_by_username(username)
        
        # Verify password if user exists
        if user_data:
            # bcrypt.checkpw performs timing-safe comparison
            # Both arguments must be bytes
            password_matches = bcrypt.checkpw(
                password.encode('utf-8'),                    # Plain password as bytes
                user_data['password_hash'].encode('utf-8')   # Stored hash as bytes
            )
            
            if password_matches:
                # Update last login timestamp for user activity tracking
                update_last_login(user_data['id'])
                
                # Log successful authentication
                logging.info(f"User logged in: {username}")
                
                # Create and return User object for Flask-Login
                return User(
                    user_id=user_data['id'],
                    username=user_data['username'],
                    email=user_data['email'],
                    is_admin=bool(user_data['is_admin'])
                )
        
        # Authentication failed - log warning for security monitoring
        # Note: We don't specify whether username or password was wrong
        # to prevent username enumeration attacks
        logging.warning(f"Failed login attempt for username: {username}")
        
        return None
    
    @staticmethod
    def register(username, email, password):
        """
        Register a new user account.
        
        This method:
        1. Checks if username/email already exists
        2. Hashes the password using bcrypt
        3. Creates the user in the database
        4. Logs the registration event
        
        Password Hashing:
            - Uses bcrypt with automatic salt generation
            - Work factor is bcrypt default (currently 12 rounds)
            - Salt is included in the hash string
        
        Args:
            username (str): Desired username for the new account.
                Must be unique. Should be pre-validated.
            
            email (str): User's email address.
                Must be unique. Should be pre-validated for format.
            
            password (str): Plain-text password.
                Should be pre-validated for strength requirements.
                Will be hashed before storage.
        
        Returns:
            tuple: A tuple of (success, message)
                - success (bool): True if registration succeeded
                - message (str): User-friendly result message
        
        Return Values:
            (False, 'Username or email already exists.'): Duplicate found
            (False, 'An error occurred during registration.'): Database error
            (True, 'Registration successful! Please log in.'): Success
        
        Example:
            >>> success, message = AuthService.register(
            ...     username='newuser',
            ...     email='new@example.com',
            ...     password='SecurePass123'
            ... )
            >>> if success:
            ...     flash(message, 'success')
            ...     return redirect(url_for('auth.login'))
            ... else:
            ...     flash(message, 'danger')
        
        Logging:
            - INFO: "New user registered: {username}" on success
        """
        # --------------------------------------------------------------------------
        # Check for existing user with same username or email
        # --------------------------------------------------------------------------
        if user_exists(username, email):
            return False, 'Username or email already exists.'
        
        # --------------------------------------------------------------------------
        # Hash password using bcrypt
        # --------------------------------------------------------------------------
        # bcrypt.gensalt() generates a random salt
        # bcrypt.hashpw() creates the hash with the salt embedded
        # Result is bytes, decode to string for database storage
        password_hash = bcrypt.hashpw(
            password.encode('utf-8'),   # Password must be bytes
            bcrypt.gensalt()             # Generate random salt
        ).decode('utf-8')                # Convert bytes to string for storage
        
        # --------------------------------------------------------------------------
        # Create user in database
        # --------------------------------------------------------------------------
        if create_user(username, email, password_hash):
            # Log successful registration
            logging.info(f"New user registered: {username}")
            return True, 'Registration successful! Please log in.'
        
        # Database operation failed
        return False, 'An error occurred during registration.'
