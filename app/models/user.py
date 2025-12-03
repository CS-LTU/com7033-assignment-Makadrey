"""
User Model Module
=================

Defines the User class for authentication and session management.

This module implements the User entity that represents authenticated
users in the system. The User class integrates with Flask-Login to
provide seamless session management.

Flask-Login Integration:
    The User class inherits from UserMixin, which provides default
    implementations for:
    - is_authenticated: Returns True (user is logged in)
    - is_active: Returns True (account is not disabled)
    - is_anonymous: Returns False (this is a real user)
    - get_id(): Returns the user ID as a string

User Roles:
    - Regular User (is_admin=False): Can view/manage patients
    - Admin User (is_admin=True): Can also manage other users

Usage:
    >>> from app.models.user import User
    >>> user = User(user_id=1, username='admin', email='admin@test.com', is_admin=True)
    >>> print(user.is_authenticated)  # True
    >>> print(user.get_id())  # '1'

Author: Healthcare Data Management System
Version: 2.0.0
"""

from flask_login import UserMixin


class User(UserMixin):
    """
    User model for authentication and session management.
    
    This class represents an authenticated user in the system.
    It does NOT handle database operations - those are in sqlite_db.py.
    
    Flask-Login Integration:
        Inherits from UserMixin which provides:
        - is_authenticated: Property that returns True
        - is_active: Property that returns True
        - is_anonymous: Property that returns False
        - get_id(): Method to return user ID (we override this)
    
    Attributes:
        id (int): Unique user identifier (primary key in database)
        username (str): User's login username (unique)
        email (str): User's email address (unique)
        is_admin (bool): Whether user has admin privileges
    
    Example:
        >>> user = User(
        ...     user_id=1,
        ...     username='johndoe',
        ...     email='john@example.com',
        ...     is_admin=False
        ... )
        >>> print(user)
        <User johndoe>
        >>> print(user.is_authenticated)
        True
    """
    
    def __init__(self, user_id, username, email, is_admin=False):
        """
        Initialize a User instance.
        
        Creates a User object representing an authenticated user.
        This constructor is typically called by get_user_by_id()
        when loading a user from the database.
        
        Args:
            user_id (int): Unique user identifier from database.
                This becomes the 'id' attribute used by Flask-Login.
            
            username (str): User's login username.
                Must be unique in the database.
                Used for display and login.
            
            email (str): User's email address.
                Must be unique in the database.
                Used for notifications and password recovery.
            
            is_admin (bool, optional): Admin privileges flag.
                Defaults to False.
                True = Can access admin panel and manage users
                False = Regular user, can only manage patients
        
        Example:
            >>> # Creating a regular user
            >>> user = User(1, 'johndoe', 'john@example.com')
            >>> user.is_admin
            False
            
            >>> # Creating an admin user
            >>> admin = User(2, 'admin', 'admin@example.com', is_admin=True)
            >>> admin.is_admin
            True
        """
        # Store user ID - used by Flask-Login for session management
        self.id = user_id
        
        # Store username - used for display and authentication
        self.username = username
        
        # Store email - used for user identification
        self.email = email
        
        # Store admin flag - used for authorization checks
        self.is_admin = is_admin
    
    def get_id(self):
        """
        Return the user ID as a string for Flask-Login.
        
        Flask-Login requires this method to return a unicode string
        that uniquely identifies the user. This ID is stored in the
        session cookie and used to reload the user on each request.
        
        Returns:
            str: The user's ID converted to a string.
        
        Note:
            Flask-Login always expects a string, even if the ID
            is stored as an integer in the database.
        
        Example:
            >>> user = User(user_id=42, username='test', email='test@test.com')
            >>> user.get_id()
            '42'
            >>> type(user.get_id())
            <class 'str'>
        """
        return str(self.id)
    
    def __repr__(self):
        """
        Return a string representation of the User for debugging.
        
        This method is called when you print() a User object or
        when it appears in log messages.
        
        Returns:
            str: A string in the format '<User username>'
        
        Example:
            >>> user = User(1, 'admin', 'admin@test.com')
            >>> print(user)
            <User admin>
            >>> repr(user)
            '<User admin>'
        """
        return f'<User {self.username}>'
    
    def __eq__(self, other):
        """
        Check equality between two User objects.
        
        Two users are equal if they have the same ID.
        
        Args:
            other: Another object to compare with
        
        Returns:
            bool: True if both are User objects with the same ID
        
        Example:
            >>> user1 = User(1, 'admin', 'admin@test.com')
            >>> user2 = User(1, 'admin', 'admin@test.com')
            >>> user1 == user2
            True
        """
        if isinstance(other, User):
            return self.id == other.id
        return False
    
    def __hash__(self):
        """
        Return hash value for the User.
        
        Allows User objects to be used in sets and as dictionary keys.
        
        Returns:
            int: Hash based on user ID
        """
        return hash(self.id)
