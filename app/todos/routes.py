from datetime import datetime
from flask import jsonify, request
from marshmallow import ValidationError
from sqlalchemy import select

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


# ── LIST ──────────────────────────────────────────────────────
@todos_bp.route('', methods=['GET'])
def list_todos():
    """
    Build a query using SQLAlchemy's select().
    Filters are chained onto the query before execution —
    only one SQL query hits the database no matter how
    many filters are applied.
    """
    stmt = select(Todo).order_by(Todo.created_at.desc())

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
def create_todo():
    raw_data = request.get_json()
    if not raw_data:
        return jsonify({'error': 'Request body must be JSON.', 'code': 'BAD_REQUEST'}), 400

    data = todo_create_schema.load(raw_data)

    # Instantiate the model — SQLAlchemy sets defaults (id, created_at, etc.)
    todo = Todo(title=data['title'], priority=data['priority'], notes=data['notes'])

    db.session.add(todo)      # stage the INSERT
    db.session.commit()       # write to database

    return jsonify(todo_schema.dump(todo.to_dict())), 201


# ── GET ONE ───────────────────────────────────────────────────
@todos_bp.route('/<string:todo_id>', methods=['GET'])
def get_todo(todo_id):
    todo, err = _get_or_404(todo_id)
    if err:
        return err

    return jsonify(todo_schema.dump(todo.to_dict())), 200


# ── REPLACE (PUT) ─────────────────────────────────────────────
@todos_bp.route('/<string:todo_id>', methods=['PUT'])
def replace_todo(todo_id):
    todo, err = _get_or_404(todo_id)
    if err:
        return err

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
def update_todo(todo_id):
    todo, err = _get_or_404(todo_id)
    if err:
        return err

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
def delete_todo(todo_id):
    todo, err = _get_or_404(todo_id)
    if err:
        return err

    db.session.delete(todo)   # stage the DELETE
    db.session.commit()       # write to database
    return '', 204