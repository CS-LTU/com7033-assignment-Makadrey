"""
SQLite Database Module
======================

Handles all SQLite database operations for user authentication.

This module manages the users database, which stores authentication
credentials and user profiles. SQLite is chosen for user data because:

1. Simple setup - no separate database server needed
2. Lightweight - suitable for user data (typically small dataset)
3. ACID compliant - ensures data integrity
4. File-based - easy backup and migration

Database Schema:
    users table:
        - id: INTEGER PRIMARY KEY (auto-increment)
        - username: TEXT UNIQUE NOT NULL
        - email: TEXT UNIQUE NOT NULL
        - password_hash: TEXT NOT NULL (bcrypt hash)
        - is_admin: BOOLEAN DEFAULT 0
        - created_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        - last_login: TIMESTAMP

Security Notes:
    - Passwords are NEVER stored in plain text
    - bcrypt is used for password hashing (adaptive, salted)
    - Parameterized queries prevent SQL injection
    - Connection is closed after each operation

Usage:
    >>> from app.database.sqlite_db import get_user_by_username
    >>> user = get_user_by_username('admin')
    >>> print(user['email'])

Author: Healthcare Data Management System
Version: 2.0.0
"""

import sqlite3
import logging
from datetime import datetime

import bcrypt
from flask import current_app

from app.models.user import User


# =============================================================================
# DATABASE CONNECTION
# =============================================================================

def get_db_connection():
    """
    Create and return a new SQLite database connection.
    
    This function creates a new connection for each database operation.
    While connection pooling would be more efficient, SQLite handles
    concurrent connections well for our use case.
    
    The Row factory is set to allow dictionary-style access to columns:
        >>> row['username'] instead of row[1]
    
    Returns:
        sqlite3.Connection: Database connection object with Row factory
            configured for dictionary-style column access
    
    Raises:
        sqlite3.Error: If database file cannot be opened/created
    
    Example:
        >>> conn = get_db_connection()
        >>> cursor = conn.cursor()
        >>> cursor.execute('SELECT * FROM users')
        >>> conn.close()
    
    Note:
        Always close the connection after use to release file lock.
        Uses current_app.config for database path (requires app context).
    """
    # Get database path from Flask config, with fallback default
    db_path = current_app.config.get('SQLITE_DB_PATH', 'users.db')
    
    # Create connection to SQLite database file
    # If file doesn't exist, SQLite will create it
    conn = sqlite3.connect(db_path)
    
    # Enable dictionary-style access to rows
    # row['column_name'] instead of row[index]
    conn.row_factory = sqlite3.Row
    
    return conn


# =============================================================================
# DATABASE INITIALIZATION
# =============================================================================

def init_sqlite_db():
    """
    Initialize the SQLite database schema and seed data.
    
    This function performs first-time database setup:
    1. Creates the users table if it doesn't exist
    2. Creates a default admin user if no users exist
    
    Called automatically by the application factory on startup.
    Safe to call multiple times (idempotent).
    
    Default Admin Credentials:
        Username: admin
        Password: admin123
        Email: admin@hospital.com
    
    WARNING:
        Change the default admin password immediately after first login!
        The default password is for initial setup only.
    
    Table Schema:
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            is_admin BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    
    Raises:
        sqlite3.Error: If database operations fail
    """
    # Get database path from config
    db_path = current_app.config.get('SQLITE_DB_PATH', 'users.db')
    
    # Create connection (creates file if not exists)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # --------------------------------------------------------------------------
    # Create users table with secure schema
    # --------------------------------------------------------------------------
    # IF NOT EXISTS prevents error if table already exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            is_admin BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')
    
    # --------------------------------------------------------------------------
    # Seed default admin user if database is empty
    # --------------------------------------------------------------------------
    cursor.execute('SELECT COUNT(*) FROM users')
    user_count = cursor.fetchone()[0]
    
    if user_count == 0:
        # Hash the default admin password using bcrypt
        # bcrypt automatically generates a salt and includes it in the hash
        admin_password = bcrypt.hashpw(
            'admin123'.encode('utf-8'),  # Default password
            bcrypt.gensalt()              # Generate random salt
        )
        
        # Insert default admin user
        cursor.execute(
            'INSERT INTO users (username, email, password_hash, is_admin) VALUES (?, ?, ?, ?)',
            ('admin', 'admin@hospital.com', admin_password.decode('utf-8'), 1)
        )
        
        logging.info("Default admin user created (username: admin, password: admin123)")
    
    # Commit changes and close connection
    conn.commit()
    conn.close()


# =============================================================================
# USER RETRIEVAL FUNCTIONS
# =============================================================================

def get_user_by_id(user_id):
    """
    Retrieve a user by their unique ID.
    
    Used by Flask-Login's user_loader callback to restore user
    sessions. Called on every request that accesses current_user.
    
    Args:
        user_id (int|str): The user's unique identifier.
            Flask-Login passes this as a string, but SQLite handles conversion.
    
    Returns:
        User: User object with id, username, email, is_admin attributes.
            Implements Flask-Login's UserMixin interface.
        
        None: If no user found with the given ID
    
    Example:
        >>> user = get_user_by_id(1)
        >>> if user:
        ...     print(f"Found user: {user.username}")
        ... else:
        ...     print("User not found")
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Use parameterized query to prevent SQL injection
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user_data = cursor.fetchone()
    
    conn.close()
    
    # Convert database row to User object if found
    if user_data:
        return User(
            user_id=user_data['id'],
            username=user_data['username'],
            email=user_data['email'],
            is_admin=bool(user_data['is_admin'])  # SQLite stores as 0/1
        )
    
    return None


def get_user_by_username(username):
    """
    Retrieve a user by their username.
    
    Used during login to find the user and verify their password.
    Returns the raw database row (not User object) to access password_hash.
    
    Args:
        username (str): The username to search for (case-sensitive)
    
    Returns:
        sqlite3.Row: Dictionary-like row with all user columns:
            - id, username, email, password_hash, is_admin, created_at, last_login
            Access via: row['column_name']
        
        None: If no user found with the given username
    
    Example:
        >>> user_row = get_user_by_username('admin')
        >>> if user_row:
        ...     print(f"User email: {user_row['email']}")
        ...     # Verify password
        ...     bcrypt.checkpw(password, user_row['password_hash'])
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Parameterized query prevents SQL injection
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user_data = cursor.fetchone()
    
    conn.close()
    
    return user_data


def get_all_users():
    """
    Retrieve all users for the admin panel.
    
    Returns user data without password hashes for security.
    Results are ordered by ID (registration order).
    
    Returns:
        list[sqlite3.Row]: List of user rows, each containing:
            - id, username, email, is_admin, created_at, last_login
            Note: password_hash is NOT included for security
    
    Example:
        >>> users = get_all_users()
        >>> for user in users:
        ...     print(f"{user['username']} - Admin: {user['is_admin']}")
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Select only non-sensitive fields (no password_hash)
    cursor.execute('''
        SELECT id, username, email, is_admin, created_at, last_login 
        FROM users 
        ORDER BY id
    ''')
    users = cursor.fetchall()
    
    conn.close()
    
    return users


# =============================================================================
# USER CREATION AND VALIDATION
# =============================================================================

def create_user(username, email, password_hash):
    """
    Create a new user in the database.
    
    This function only handles database insertion. Password hashing
    should be done by the caller (auth_service.py).
    
    Args:
        username (str): Unique username (will fail if duplicate)
        email (str): Unique email address (will fail if duplicate)
        password_hash (str): Pre-hashed password (bcrypt hash as string)
    
    Returns:
        bool: True if user created successfully, False on error
    
    Raises:
        Does not raise - catches exceptions and returns False
    
    Example:
        >>> password_hash = bcrypt.hashpw(b'password', bcrypt.gensalt()).decode()
        >>> success = create_user('newuser', 'new@email.com', password_hash)
        >>> if success:
        ...     print("User created!")
    
    Note:
        - Check user_exists() before calling to provide better error messages
        - Caller is responsible for input validation
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Insert new user (is_admin defaults to 0/False)
        cursor.execute(
            'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
            (username, email, password_hash)
        )
        
        conn.commit()
        conn.close()
        
        return True
        
    except sqlite3.IntegrityError as e:
        # Duplicate username or email
        logging.warning(f"User creation failed (duplicate): {e}")
        return False
        
    except Exception as e:
        # Other database errors
        logging.error(f"Error creating user: {e}")
        return False


def user_exists(username, email):
    """
    Check if a user with the given username OR email already exists.
    
    Used during registration to provide specific error messages
    before attempting to create the user.
    
    Args:
        username (str): Username to check
        email (str): Email to check
    
    Returns:
        bool: True if a user exists with either the username or email,
              False if neither exists in the database
    
    Example:
        >>> if user_exists('admin', 'test@test.com'):
        ...     flash('Username or email already taken')
        ... else:
        ...     create_user(...)
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check for either username or email match
    cursor.execute(
        'SELECT id FROM users WHERE username = ? OR email = ?', 
        (username, email)
    )
    exists = cursor.fetchone() is not None
    
    conn.close()
    
    return exists


# =============================================================================
# USER UPDATE FUNCTIONS
# =============================================================================

def update_last_login(user_id):
    """
    Update the user's last_login timestamp to current time.
    
    Called after successful login to track user activity.
    
    Args:
        user_id (int): The user's unique identifier
    
    Example:
        >>> # After successful password verification
        >>> update_last_login(user.id)
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Update last_login to current timestamp
    cursor.execute(
        'UPDATE users SET last_login = ? WHERE id = ?', 
        (datetime.now(), user_id)
    )
    
    conn.commit()
    conn.close()
