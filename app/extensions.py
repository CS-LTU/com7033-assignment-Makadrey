"""
Flask Extensions Module
=======================

Initializes Flask extensions separately from the application factory
to prevent circular import issues.

Problem Solved:
    When extensions are created inside the app factory, any module that
    imports from the extension before the app is created will fail.
    By creating extensions here without binding them to an app, other
    modules can import them safely.

Pattern Used:
    1. Create extension instances without app (this module)
    2. Bind extensions to app in create_app() factory
    3. Other modules import extensions from here

Extensions Configured:
    - Flask-Login: User session management and authentication

Flask-Login Overview:
    Flask-Login provides user session management, handling:
    - User login/logout
    - "Remember me" functionality
    - Session protection against tampering
    - @login_required decorator for route protection
    - current_user proxy for accessing logged-in user

Usage:
    >>> from app.extensions import login_manager
    >>> login_manager.init_app(app)  # In app factory

Author: Healthcare Data Management System
Version: 2.0.0
"""

from flask_login import LoginManager

# =============================================================================
# FLASK-LOGIN CONFIGURATION
# =============================================================================

# Create LoginManager instance
# This manages user sessions and provides authentication utilities
login_manager = LoginManager()

# The view function name to redirect to when login is required
# Format: 'blueprint_name.view_function_name'
login_manager.login_view = 'auth.login'

# Message flashed when user needs to log in
# Displayed with flash() when @login_required redirects
login_manager.login_message = 'Please log in to access this page.'

# Category for the login message (used for styling alerts)
# Options: 'info', 'success', 'warning', 'danger'
login_manager.login_message_category = 'info'

# Session protection level
# 'basic': Checks if user agent changed
# 'strong': Also checks IP address; logs out on mismatch
# None: Disables session protection
login_manager.session_protection = 'strong'


# =============================================================================
# USER LOADER CALLBACK
# =============================================================================

@login_manager.user_loader
def load_user(user_id):
    """
    Load a user from the database by their ID.
    
    This callback is used by Flask-Login to reload the user object
    from the user ID stored in the session. It's called on every
    request that accesses current_user.
    
    How it works:
        1. User logs in -> user.id stored in session
        2. On each request -> Flask-Login calls this function
        3. Function returns User object -> available as current_user
        4. If None returned -> user is treated as anonymous
    
    Args:
        user_id (str): The user ID stored in the session cookie.
            Note: Flask-Login always passes this as a string.
    
    Returns:
        User: User object if found in database, implementing:
            - is_authenticated: True if user is logged in
            - is_active: True if user account is active
            - is_anonymous: False for real users
            - get_id(): Returns string user ID
        
        None: If user ID not found in database
            (causes Flask-Login to treat user as anonymous)
    
    Example:
        >>> user = load_user('1')
        >>> print(user.username)
        'admin'
        >>> print(user.is_authenticated)
        True
    
    Note:
        Import is done inside function to avoid circular imports.
        The database module imports from extensions, so we can't
        import database at module level.
    """
    # Import inside function to avoid circular import
    # sqlite_db.py may import from app.extensions
    from app.database.sqlite_db import get_user_by_id
    
    # Query database for user with given ID
    # Returns User object or None if not found
    return get_user_by_id(user_id)
