from flask import Blueprint

# Create the Blueprint.
# First arg  = name (used internally by Flask, url_for, etc.)
# Second arg = where Flask looks for templates/static files
todos_bp = Blueprint('todos', __name__)

# Import routes AFTER creating the blueprint to avoid
# circular imports. The routes module needs todos_bp,
# so todos_bp must exist before routes.py is imported.
from app.todos import routes  # noqa: E402, F401