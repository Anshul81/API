from datetime import datetime
from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from marshmallow import ValidationError
from sqlalchemy import select
from app.auth.decorator import admin_required
from app.extensions import db
from app.todos import todos_bp
from app.todos.models import Todo
from app.todos.schemas import (
    todo_schema, todos_schema,
    todo_create_schema, todo_update_schema
)


def _get_or_404(todo_id: str):
    """Fetch a Todo by primary key or return a 404 response."""
    todo = db.session.get(Todo, todo_id)
    if todo is None:
        return None, (jsonify({
            'error': f"Todo '{todo_id}' not found.",
            'code':  'NOT_FOUND'
        }), 404)
    return todo, None

def _owns_or_admin(todo, user_id, role):
    return todo.user_id == user_id or role == 'admin'

# ── LIST ──────────────────────────────────────────────────────
@todos_bp.route('', methods=['GET'])
@jwt_required()
def list_todos():
    """
    Build a query using SQLAlchemy's select().
    Filters are chained onto the query before execution —
    only one SQL query hits the database no matter how
    many filters are applied.
    """

    user_id = get_jwt_identity()
    claims = get_jwt()
    role = claims.get('role')

    stmt = select(Todo).order_by(Todo.created_at.desc())

    if role != 'admin':
        stmt = stmt.where(Todo.user_id == user_id)

    # Filter by ?done=true or ?done=false
    done_filter = request.args.get('done')
    if done_filter is not None:
        is_done = done_filter.lower() == 'true'
        stmt    = stmt.where(Todo.done == is_done)

    # Filter by ?priority=high|medium|low
    priority_filter = request.args.get('priority')
    if priority_filter:
        stmt = stmt.where(Todo.priority == priority_filter)

    # Execute the query — scalars() unwraps the Row wrappers
    todos = db.session.execute(stmt).scalars().all()

    return jsonify({
        'todos': todos_schema.dump([t.to_dict() for t in todos]),
        'count': len(todos)
    }), 200


# ── CREATE ────────────────────────────────────────────────────
@todos_bp.route('', methods=['POST'])
@jwt_required()
def create_todo():
    user_id = get_jwt_identity()

    raw_data = request.get_json()
    if not raw_data:
        return jsonify({'error': 'Request body must be JSON.', 'code': 'BAD_REQUEST'}), 400

    data = todo_create_schema.load(raw_data)

    # Instantiate the model — SQLAlchemy sets defaults (id, created_at, etc.)
    todo = Todo(
        title=data['title'],
        priority=data['priority'],
        notes=data['notes'],
        user_id=user_id)

    db.session.add(todo)      # stage the INSERT
    db.session.commit()       # write to database

    return jsonify(todo_schema.dump(todo.to_dict())), 201


# ── GET ONE ───────────────────────────────────────────────────
@todos_bp.route('/<string:todo_id>', methods=['GET'])
@jwt_required()
def get_todo(todo_id):
    user_id = get_jwt_identity()
    claims = get_jwt()
    todo, err = _get_or_404(todo_id)
    if err:
        return err

    if not _owns_or_admin(todo, user_id, claims.get('role')):
        return jsonify({'error': "Access Denied", 'code': 'FORBIDDEN'}), 403

    return jsonify(todo_schema.dump(todo.to_dict())), 200


# ── REPLACE (PUT) ─────────────────────────────────────────────
@todos_bp.route('/<string:todo_id>', methods=['PUT'])
@jwt_required()
def replace_todo(todo_id):
    user_id = get_jwt_identity()
    claims = get_jwt()
    todo, err = _get_or_404(todo_id)
    if err:
        return err
    if not _owns_or_admin(todo, user_id, claims.get('role')):
        return jsonify({'error': "Access Denied", 'code': 'FORBIDDEN'}), 403

    raw_data = request.get_json()
    if not raw_data:
        return jsonify({'error': 'Request body must be JSON.', 'code': 'BAD_REQUEST'}), 400

    data = todo_update_schema.load(raw_data)

    if 'title' not in data:
        raise ValidationError({'title': ['Title is required for a full replace (PUT).']})

    # Directly set attributes on the ORM object.
    # SQLAlchemy tracks changes — on commit it generates
    # an UPDATE only for the columns that actually changed.
    todo.title    = data['title']
    todo.done     = data.get('done', todo.done)
    todo.priority = data.get('priority', todo.priority)
    # updated_at is handled automatically by onupdate=datetime.utcnow

    db.session.commit()
    return jsonify(todo_schema.dump(todo.to_dict())), 200


# ── PARTIAL UPDATE (PATCH) ────────────────────────────────────
@todos_bp.route('/<string:todo_id>', methods=['PATCH'])
@jwt_required()
def update_todo(todo_id):
    user_id = get_jwt_identity()
    claims = get_jwt()
    todo, err = _get_or_404(todo_id)
    if err:
        return err
    if not _owns_or_admin(todo, user_id, claims.get('role')):
        return jsonify({'error': "Access Denied", 'code': 'FORBIDDEN'}), 403

    raw_data = request.get_json()
    if not raw_data:
        return jsonify({'error': 'Request body must be JSON.', 'code': 'BAD_REQUEST'}), 400

    data = todo_update_schema.load(raw_data, partial=True)

    if not data:
        return jsonify({
            'error': 'No valid fields provided to update.',
            'code':  'BAD_REQUEST'
        }), 400

    # Only set the attributes that were actually sent
    for field, value in data.items():
        setattr(todo, field, value)

    db.session.commit()
    return jsonify(todo_schema.dump(todo.to_dict())), 200


# ── DELETE ────────────────────────────────────────────────────
@todos_bp.route('/<string:todo_id>', methods=['DELETE'])
@jwt_required()
def delete_todo(todo_id):
    user_id = get_jwt_identity()
    claims = get_jwt()
    todo, err = _get_or_404(todo_id)
    if err:
        return err
    if not _owns_or_admin(todo, user_id, claims.get('role')):
        return jsonify({'error': "Access Denied", 'code': 'FORBIDDEN'}), 403

    db.session.delete(todo)   # stage the DELETE
    db.session.commit()       # write to database
    return '', 204