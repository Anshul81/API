import os
import uuid
from datetime import datetime
from flask import Flask, jsonify, request
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret')

# ──────────────────────────────────────────
# In-memory data store
#
# A dict keyed by UUID strings. In Chapter 5
# this entire block gets replaced by SQLAlchemy.
# Using a dict now teaches you the API layer
# without database complexity getting in the way.
# ──────────────────────────────────────────
todos = {}


# ──────────────────────────────────────────
# Helper — build a consistent todo dict
# Having one factory function means if we
# change the shape later, we change it here only.
# ──────────────────────────────────────────
def make_todo(title, priority='medium'):
    todo_id = str(uuid.uuid4())
    return {
        'id':         todo_id,
        'title':      title,
        'done':       False,
        'priority':   priority,          # 'low' | 'medium' | 'high'
        'created_at': datetime.utcnow().isoformat() + 'Z',
        'updated_at': datetime.utcnow().isoformat() + 'Z',
    }


# ──────────────────────────────────────────
# Helper — find a todo or return a 404 response
# We'll use this in every endpoint that needs
# a specific todo. DRY (Don't Repeat Yourself).
# ──────────────────────────────────────────
def get_todo_or_404(todo_id):
    todo = todos.get(todo_id)
    if todo is None:
        return None, (jsonify({
            'error': f"Todo '{todo_id}' not found.",
            'code':  'NOT_FOUND'
        }), 404)
    return todo, None


# ══════════════════════════════════════════
# ENDPOINT 1: List all todos
# GET /todos
# ══════════════════════════════════════════
@app.route('/todos', methods=['GET'])
def list_todos():
    """
    Return all todos as a list.

    Optional query params:
      ?done=true     → only completed todos
      ?priority=high → filter by priority
    """
    result = list(todos.values())

    # Filter by ?done=true or ?done=false
    done_filter = request.args.get('done')
    if done_filter is not None:
        is_done = done_filter.lower() == 'true'
        result = [t for t in result if t['done'] == is_done]

    # Filter by ?priority=high|medium|low
    priority_filter = request.args.get('priority')
    if priority_filter:
        result = [t for t in result if t['priority'] == priority_filter]

    return jsonify({
        'todos': result,
        'count': len(result)
    }), 200


# ══════════════════════════════════════════
# ENDPOINT 2: Create a todo
# POST /todos
# ══════════════════════════════════════════
@app.route('/todos', methods=['POST'])
def create_todo():
    """
    Create a new todo.

    Required body: { "title": "Buy milk" }
    Optional body: { "priority": "high" }   (default: "medium")

    Returns 201 Created with the new todo object.
    201 (not 200) signals to the client that a
    new resource was created — important distinction.
    """
    data = request.get_json()

    # Validate: body must be JSON
    if not data:
        return jsonify({
            'error': 'Request body must be JSON.',
            'code':  'BAD_REQUEST'
        }), 400

    # Validate: title is required
    title = data.get('title', '').strip()
    if not title:
        return jsonify({
            'error': "'title' is required and cannot be blank.",
            'code':  'VALIDATION_ERROR'
        }), 400

    # Validate: priority must be one of the allowed values
    priority = data.get('priority', 'medium').lower()
    if priority not in ('low', 'medium', 'high'):
        return jsonify({
            'error': "'priority' must be 'low', 'medium', or 'high'.",
            'code':  'VALIDATION_ERROR'
        }), 400

    todo = make_todo(title, priority)
    todos[todo['id']] = todo

    return jsonify(todo), 201   # ← 201 Created, not 200


# ══════════════════════════════════════════
# ENDPOINT 3: Get a single todo
# GET /todos/<id>
# ══════════════════════════════════════════
@app.route('/todos/<string:todo_id>', methods=['GET'])
def get_todo(todo_id):
    """
    Fetch one todo by its UUID.
    Returns 404 if the ID doesn't exist.
    """
    todo, err = get_todo_or_404(todo_id)
    if err:
        return err

    return jsonify(todo), 200


# ══════════════════════════════════════════
# ENDPOINT 4: Full replace (PUT)
# PUT /todos/<id>
# ══════════════════════════════════════════
@app.route('/todos/<string:todo_id>', methods=['PUT'])
def replace_todo(todo_id):
    """
    Completely replace a todo.
    ALL fields are required — missing fields are set to defaults.

    Use PUT when the client owns the full state of the resource.
    """
    todo, err = get_todo_or_404(todo_id)
    if err:
        return err

    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body must be JSON.', 'code': 'BAD_REQUEST'}), 400

    title = data.get('title', '').strip()
    if not title:
        return jsonify({'error': "'title' is required.", 'code': 'VALIDATION_ERROR'}), 400

    priority = data.get('priority', 'medium').lower()
    if priority not in ('low', 'medium', 'high'):
        return jsonify({'error': "'priority' must be low/medium/high.", 'code': 'VALIDATION_ERROR'}), 400

    # Replace the entire object (preserving id and created_at)
    todos[todo_id] = {
        'id':         todo_id,
        'title':      title,
        'done':       bool(data.get('done', False)),
        'priority':   priority,
        'created_at': todo['created_at'],          # never changes
        'updated_at': datetime.utcnow().isoformat() + 'Z',
    }

    return jsonify(todos[todo_id]), 200


# ══════════════════════════════════════════
# ENDPOINT 5: Partial update (PATCH)
# PATCH /todos/<id>
# ══════════════════════════════════════════
@app.route('/todos/<string:todo_id>', methods=['PATCH'])
def update_todo(todo_id):
    """
    Partially update a todo.
    Only send the fields you want to change.

    Example: {"done": true}
    This marks it complete without touching title or priority.
    """
    todo, err = get_todo_or_404(todo_id)
    if err:
        return err

    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body must be JSON.', 'code': 'BAD_REQUEST'}), 400

    # Only update fields that were actually sent
    if 'title' in data:
        title = data['title'].strip()
        if not title:
            return jsonify({'error': "'title' cannot be blank.", 'code': 'VALIDATION_ERROR'}), 400
        todo['title'] = title

    if 'done' in data:
        todo['done'] = bool(data['done'])

    if 'priority' in data:
        if data['priority'] not in ('low', 'medium', 'high'):
            return jsonify({'error': "'priority' must be low/medium/high.", 'code': 'VALIDATION_ERROR'}), 400
        todo['priority'] = data['priority']

    todo['updated_at'] = datetime.utcnow().isoformat() + 'Z'

    return jsonify(todo), 200


# ══════════════════════════════════════════
# ENDPOINT 6: Delete a todo
# DELETE /todos/<id>
# ══════════════════════════════════════════
@app.route('/todos/<string:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    """
    Delete a todo by ID.

    Returns 204 No Content — notice there's NO body.
    204 means "it worked, there's nothing to tell you."
    Sending a body with 204 is technically invalid HTTP.
    """
    todo, err = get_todo_or_404(todo_id)
    if err:
        return err

    del todos[todo_id]

    return 'Deleted Successfully', 204   # ← empty string body, 204 status

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)