"""
Database Module
===============

Provides database connections and operations for:
- SQLite: User authentication and management
- MongoDB: Patient records and medical data
"""

from app.database.sqlite_db import (
    get_db_connection,
    init_sqlite_db,
    get_user_by_id,
    get_user_by_username,
    create_user
)

from app.database.mongo_db import (
    get_mongo_connection,
    init_mongodb
)

__all__ = [
    'get_db_connection',
    'init_sqlite_db',
    'get_user_by_id',
    'get_user_by_username',
    'create_user',
    'get_mongo_connection',
    'init_mongodb'
]

