import uuid
from datetime import datetime

# ──────────────────────────────────────────
# In-memory store
# A module-level dict that persists for the
# lifetime of the running server process.
# Restarting the server wipes all data.
# Chapter 5 replaces this with a real DB.
# ──────────────────────────────────────────
todos = {}


def make_todo(title: str, priority: str = 'medium') -> dict:
    """Create a new todo dict with a fresh UUID."""
    todo_id = str(uuid.uuid4())
    now     = datetime.utcnow().isoformat() + 'Z'
    return {
        'id':         todo_id,
        'title':      title,
        'done':       False,
        'priority':   priority,
        'created_at': now,
        'updated_at': now,
    }


def get_all_todos() -> list:
    """Return all todos as a list."""
    return list(todos.values())


def get_todo_by_id(todo_id: str) -> dict | None:
    """Return a todo by ID, or None if not found."""
    return todos.get(todo_id)


def save_todo(todo: dict) -> dict:
    """Insert or update a todo in the store."""
    todos[todo['id']] = todo
    return todo


def delete_todo_by_id(todo_id: str) -> bool:
    """Delete a todo. Returns True if deleted, False if not found."""
    if todo_id in todos:
        del todos[todo_id]
        return True
    return False