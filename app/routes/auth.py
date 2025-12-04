"""
Authentication Routes Blueprint
===============================

Handles all user authentication operations including login, logout,
and new user registration.

Routes:
    GET  /           - Home page redirect
    GET  /login      - Display login form
    POST /login      - Process login credentials
    GET  /register   - Display registration form
    POST /register   - Process new user registration
    GET  /logout     - Log out current user

Security Features:
    - CSRF protection via Flask-WTF (automatic in forms)
    - Password never logged or exposed in errors
    - Input sanitization for usernames and emails
    - Password strength validation
    - Session protection via Flask-Login
    - "next" URL validation (potential open redirect)

Flow Diagrams:
    Login Flow:
        User -> GET /login -> Display Form
        User -> POST /login -> Validate -> Authenticate -> Set Session -> Dashboard
    
    Registration Flow:
        User -> GET /register -> Display Form
        User -> POST /register -> Validate -> Create User -> Login Page

Usage:
    # In templates
    <a href="{{ url_for('auth.login') }}">Login</a>
    <a href="{{ url_for('auth.logout') }}">Logout</a>
    
    # In other blueprints
    from flask import redirect, url_for
    return redirect(url_for('auth.login'))

Author: Healthcare Data Management System
Version: 2.0.0
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

from app.services.auth_service import AuthService
from app.utils.validators import sanitize_input, validate_email, validate_password


# =============================================================================
# BLUEPRINT CONFIGURATION
# =============================================================================

# Create authentication blueprint
# Name 'auth' is used in url_for(): url_for('auth.login')
auth_bp = Blueprint('auth', __name__)


# =============================================================================
# HOME PAGE ROUTE
# =============================================================================

@auth_bp.route('/')
def index():
    """
    Home page route - smart redirect based on authentication status.
    
    Behavior:
        - Authenticated users -> Dashboard
        - Unauthenticated users -> Login page
    
    Returns:
        Response: HTTP 302 redirect to appropriate page
    
    Example:
        Visiting http://localhost:5000/ will redirect to:
        - /dashboard (if logged in)
        - /login (if not logged in)
    """
    # Check if user has an active session
    if current_user.is_authenticated:
        # Redirect authenticated users to dashboard
        return redirect(url_for('dashboard.index'))
    
    # Redirect unauthenticated users to login
    return redirect(url_for('auth.login'))


# =============================================================================
# LOGIN ROUTE
# =============================================================================

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    User login route with secure credential verification.
    
    GET Request:
        Displays the login form template.
        If user is already authenticated, redirects to dashboard.
    
    POST Request:
        Processes login credentials:
        1. Sanitizes username input (prevents XSS)
        2. Validates both fields are provided
        3. Authenticates via AuthService
        4. Creates session with Flask-Login
        5. Redirects to 'next' URL or dashboard
    
    Form Fields Expected:
        - username: User's login name
        - password: User's password (plain text over HTTPS)
    
    Query Parameters:
        - next: Optional URL to redirect to after login
                Set automatically by @login_required decorator
    
    Returns:
        GET: Rendered login.html template
        POST (success): Redirect to dashboard or 'next' URL
        POST (failure): Rendered login.html with error flash
    
    Flash Messages:
        - 'danger': "Please provide both username and password."
        - 'danger': "Invalid username or password."
        - 'success': "Welcome back, {username}!"
    
    Security Notes:
        - Password is NOT sanitized (preserves special chars)
        - Same error for wrong username OR password (prevents enumeration)
        - 'next' parameter should be validated for open redirect attacks
    
    Example:
        # Login form submission
        POST /login
        Content-Type: application/x-www-form-urlencoded
        
        username=admin&password=admin123
    """
    # --------------------------------------------------------------------------
    # Already Authenticated Check
    # --------------------------------------------------------------------------
    # If user is already logged in, no need to show login form
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    # --------------------------------------------------------------------------
    # Handle POST Request (Form Submission)
    # --------------------------------------------------------------------------
    if request.method == 'POST':
        # Sanitize username to prevent XSS (but not password - needs special chars)
        username = sanitize_input(request.form.get('username', ''))
        password = request.form.get('password', '')  # Don't sanitize password!
        
        # Validate required fields
        if not username or not password:
            flash('Please provide both username and password.', 'danger')
            return render_template('auth/login.html')
        
        # Attempt authentication via service layer
        user = AuthService.authenticate(username, password)
        
        if user:
            # Authentication successful - create session
            # login_user() stores user ID in session cookie
            login_user(user)
            
            # Flash welcome message
            flash(f'Welcome back, {username}!', 'success')
            
            # Handle 'next' parameter from @login_required redirects
            # TODO: Validate 'next' URL to prevent open redirect attacks
            next_page = request.args.get('next')
            
            # Redirect to requested page or default to dashboard
            if next_page:
                return redirect(next_page)
            return redirect(url_for('dashboard.index'))
        else:
            # Authentication failed
            # Generic message to prevent username enumeration
            flash('Invalid username or password.', 'danger')
    
    # --------------------------------------------------------------------------
    # Handle GET Request (Display Form)
    # --------------------------------------------------------------------------
    return render_template('auth/login.html')


# =============================================================================
# REGISTRATION ROUTE
# =============================================================================

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    New user registration route with comprehensive input validation.
    
    GET Request:
        Displays the registration form template.
        If user is already authenticated, redirects to dashboard.
    
    POST Request:
        Processes registration:
        1. Sanitizes username and email inputs
        2. Validates all required fields present
        3. Validates email format
        4. Validates password confirmation matches
        5. Validates password strength
        6. Creates user via AuthService
        7. Redirects to login on success
    
    Form Fields Expected:
        - username: Desired username (will be sanitized)
        - email: User's email address (will be sanitized)
        - password: Desired password (NOT sanitized)
        - confirm_password: Password confirmation (NOT sanitized)
    
    Validation Rules:
        - All fields required
        - Email must be valid format
        - Passwords must match
        - Password must meet strength requirements:
            * Minimum 8 characters
            * At least one uppercase letter
            * At least one lowercase letter
            * At least one digit
    
    Returns:
        GET: Rendered register.html template
        POST (success): Redirect to login page
        POST (failure): Rendered register.html with error flash
    
    Flash Messages:
        - 'danger': Various validation errors
        - 'success': "Registration successful! Please log in."
    
    Example:
        # Registration form submission
        POST /register
        Content-Type: application/x-www-form-urlencoded
        
        username=newuser&email=new@example.com&password=SecurePass123&confirm_password=SecurePass123
    """
    # --------------------------------------------------------------------------
    # Already Authenticated Check
    # --------------------------------------------------------------------------
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    # --------------------------------------------------------------------------
    # Handle POST Request (Form Submission)
    # --------------------------------------------------------------------------
    if request.method == 'POST':
        # Extract and sanitize form data
        username = sanitize_input(request.form.get('username', ''))
        email = sanitize_input(request.form.get('email', ''))
        password = request.form.get('password', '')  # Don't sanitize passwords
        confirm_password = request.form.get('confirm_password', '')
        
        # ----------------------------------------------------------------------
        # Validation: Required Fields
        # ----------------------------------------------------------------------
        if not username or not email or not password:
            flash('All fields are required.', 'danger')
            return render_template('auth/register.html')
        
        # ----------------------------------------------------------------------
        # Validation: Email Format
        # ----------------------------------------------------------------------
        if not validate_email(email):
            flash('Invalid email format.', 'danger')
            return render_template('auth/register.html')
        
        # ----------------------------------------------------------------------
        # Validation: Password Confirmation
        # ----------------------------------------------------------------------
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/register.html')
        
        # ----------------------------------------------------------------------
        # Validation: Password Strength
        # ----------------------------------------------------------------------
        is_valid, error_msg = validate_password(password)
        if not is_valid:
            flash(error_msg, 'danger')
            return render_template('auth/register.html')
        
        # ----------------------------------------------------------------------
        # Create User Account
        # ----------------------------------------------------------------------
        success, message = AuthService.register(username, email, password)
        
        if success:
            flash(message, 'success')
            return redirect(url_for('auth.login'))
        else:
            flash(message, 'danger')
    
    # --------------------------------------------------------------------------
    # Handle GET Request (Display Form)
    # --------------------------------------------------------------------------
    return render_template('auth/register.html')


# =============================================================================
# LOGOUT ROUTE
# =============================================================================

@auth_bp.route('/logout')
@login_required  # Must be logged in to log out
def logout():
    """
    User logout route - ends the current session.
    
    Behavior:
        1. Clears the user's session (Flask-Login)
        2. Flashes confirmation message
        3. Redirects to login page
    
    Decorators:
        @login_required: Ensures only authenticated users can access.
            Unauthenticated users are redirected to login.
    
    Returns:
        Response: HTTP 302 redirect to login page
    
    Flash Messages:
        - 'info': "You have been logged out successfully."
    
    Security Notes:
        - Session cookie is invalidated
        - Any "remember me" token is cleared
        - User must re-authenticate to access protected routes
    
    Example:
        # Logout link in template
        <a href="{{ url_for('auth.logout') }}">Logout</a>
    """
    # Clear the user's session
    # This removes the user ID from the session cookie
    logout_user()
    
    # Flash confirmation message
    flash('You have been logged out successfully.', 'info')
    
    # Redirect to login page
    return redirect(url_for('auth.login'))
