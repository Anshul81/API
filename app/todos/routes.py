from datetime import datetime
from flask import jsonify, request
from marshmallow import ValidationError

from app.todos import todos_bp
from app.todos.models import (
    make_todo, get_all_todos, get_todo_by_id,
    save_todo, delete_todo_by_id
)
from app.todos.schemas import (
    todo_schema, todos_schema,
    todo_create_schema, todo_update_schema
)


def _get_or_404(todo_id: str):
    todo = get_todo_by_id(todo_id)
    if todo is None:
        return None, (jsonify({
            'error': f"Todo '{todo_id}' not found.",
            'code':  'NOT_FOUND'
        }), 404)
    return todo, None


# ── LIST ──────────────────────────────────────────────────────
@todos_bp.route('', methods=['GET'])
def list_todos():
    result = get_all_todos()

    done_filter = request.args.get('done')
    if done_filter is not None:
        is_done = done_filter.lower() == 'true'
        result  = [t for t in result if t['done'] == is_done]

    priority_filter = request.args.get('priority')
    if priority_filter:
        result = [t for t in result if t['priority'] == priority_filter]

    return jsonify({
        'todos': todos_schema.dump(result),   # ← serialise through schema
        'count': len(result)
    }), 200


# ── CREATE ────────────────────────────────────────────────────
@todos_bp.route('', methods=['POST'])
def create_todo():
    """
    schema.load() does three things in one call:
      1. Parses the raw dict from request.get_json()
      2. Validates every field against the schema rules
      3. Applies defaults (priority = 'medium' if not sent)

    If validation fails → raises ValidationError →
    caught by the global handler in errors.py → 422 response.
    Your handler below only runs on clean, valid data.
    """
    raw_data = request.get_json()
    if not raw_data:
        return jsonify({'error': 'Request body must be JSON.', 'code': 'BAD_REQUEST'}), 400

    # This single line replaces all your manual validation
    data = todo_create_schema.load(raw_data)

    todo = make_todo(data['title'], data['priority'])
    save_todo(todo)

    return jsonify(todo_schema.dump(todo)), 201


# ── GET ONE ───────────────────────────────────────────────────
@todos_bp.route('/<string:todo_id>', methods=['GET'])
def get_todo(todo_id):
    todo, err = _get_or_404(todo_id)
    if err:
        return err

    return jsonify(todo_schema.dump(todo)), 200


# ── REPLACE (PUT) ─────────────────────────────────────────────
@todos_bp.route('/<string:todo_id>', methods=['PUT'])
def replace_todo(todo_id):
    todo, err = _get_or_404(todo_id)
    if err:
        return err

    raw_data = request.get_json()
    if not raw_data:
        return jsonify({'error': 'Request body must be JSON.', 'code': 'BAD_REQUEST'}), 400

    # For PUT we use TodoUpdateSchema but enforce title is present manually.
    # Why not TodoCreateSchema? Because 'done' is also a valid PUT field,
    # and TodoCreateSchema doesn't know about 'done'.
    data = todo_update_schema.load(raw_data)

    if 'title' not in data:
        raise ValidationError({'title': ['Title is required for a full replace (PUT).']})

    updated = {
        **todo,
        'title':      data['title'],
        'done':       data.get('done', todo['done']),
        'priority':   data.get('priority', todo['priority']),
        'updated_at': datetime.utcnow().isoformat() + 'Z',
    }
    save_todo(updated)
    return jsonify(todo_schema.dump(updated)), 200


# ── PARTIAL UPDATE (PATCH) ────────────────────────────────────
@todos_bp.route('/<string:todo_id>', methods=['PATCH'])
def update_todo(todo_id):
    todo, err = _get_or_404(todo_id)
    if err:
        return err

    raw_data = request.get_json()
    if not raw_data:
        return jsonify({'error': 'Request body must be JSON.', 'code': 'BAD_REQUEST'}), 400

    # load() with partial=True means no field is required —
    # only fields that are present get validated.
    # This is exactly PATCH semantics.
    data = todo_update_schema.load(raw_data, partial=True)

    if not data:
        return jsonify({
            'error': 'No valid fields provided to update.',
            'code':  'BAD_REQUEST'
        }), 400

    todo.update(data)
    todo['updated_at'] = datetime.utcnow().isoformat() + 'Z'
    save_todo(todo)

    return jsonify(todo_schema.dump(todo)), 200


# ── DELETE ────────────────────────────────────────────────────
@todos_bp.route('/<string:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    todo, err = _get_or_404(todo_id)
    if err:
        return err

    delete_todo_by_id(todo_id)
    return '', 204