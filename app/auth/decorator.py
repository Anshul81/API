# app/auth/decorators.py

from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt


def admin_required(fn):
    """
    Decorator that allows only admin users through.
    Must be used AFTER @jwt_required() — jwt_required runs
    first to verify the token, then admin_required checks the role.

    Usage:
        @jwt_required()
        @admin_required
        def my_admin_route():
            ...
    """
    @wraps(fn)    # preserves the original function name + docstring
    def wrapper(*args, **kwargs):
        claims = get_jwt()   # reads the decoded JWT payload
        if claims.get('role') != 'admin':
            return jsonify({
                'error': 'Admin access required.',
                'code':  'FORBIDDEN'
            }), 403   # 403 Forbidden — authenticated but not authorised
        return fn(*args, **kwargs)
    return wrapper