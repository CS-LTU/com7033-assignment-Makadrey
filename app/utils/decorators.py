"""
Custom Decorators
=================

Route decorators for access control and functionality.
"""

import logging
from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user


def admin_required(f):
    """
    Decorator to require admin privileges for a route.
    
    Redirects non-admin users to dashboard with error message.
    
    Args:
        f: Function to decorate
        
    Returns:
        Decorated function
        
    Usage:
        @app.route('/admin')
        @login_required
        @admin_required
        def admin_panel():
            return render_template('admin.html')
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        
        if not current_user.is_admin:
            flash('Admin privileges required to access this page.', 'danger')
            logging.warning(
                f"Unauthorized admin access attempt by user: {current_user.username}"
            )
            return redirect(url_for('dashboard.index'))
        
        return f(*args, **kwargs)
    return decorated_function


def log_activity(action):
    """
    Decorator to log user activity.
    
    Args:
        action (str): Description of the action being logged
        
    Returns:
        Decorator function
        
    Usage:
        @app.route('/delete/<id>')
        @log_activity('deleted patient record')
        def delete_patient(id):
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            username = current_user.username if current_user.is_authenticated else 'Anonymous'
            logging.info(f"User {username} {action}")
            return f(*args, **kwargs)
        return decorated_function
    return decorator

