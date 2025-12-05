"""
Admin Routes
============

Admin-only routes for user management.
"""

from flask import Blueprint, render_template
from flask_login import login_required

from app.utils.decorators import admin_required
from app.database.sqlite_db import get_all_users


admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/admin/users')
@login_required
@admin_required
def users():
    """
    Admin page to manage users (admin only).
    """
    users_list = get_all_users()
    return render_template('admin/users.html', users=users_list)

