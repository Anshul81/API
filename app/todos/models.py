import uuid
from datetime import datetime
from app.extensions import db


class Todo(db.Model):
    """
    SQLAlchemy model for the todos table.

    Inheriting from db.Model tells SQLAlchemy this class
    represents a database table. The table name defaults
    to the lowercase class name: 'todo'.
    We override it with __tablename__ for clarity.
    """
    __tablename__ = 'todos'

    # ── Columns ───────────────────────────────────────
    # primary_key=True — uniquely identifies each row
    # default=       — Python-side default (runs before INSERT)
    # nullable=False — database-side NOT NULL constraint
    # index=True     — creates a DB index for faster lookups

    id = db.Column(
        db.String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    title = db.Column(
        db.String(120),
        nullable=False
    )
    done = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )
    priority = db.Column(
        db.String(10),
        nullable=False,
        default='medium',
        index=True          # we filter by priority often
    )
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow    # note: no () — pass the function, not the result
    )
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow   # SQLAlchemy calls this automatically on UPDATE
    )

    notes = db.Column(
        db.String(250),
        nullable=True,
        default="NA"
    )

    def __repr__(self):
        """Human-readable string for debugging — shows up in logs."""
        return f'<Todo {self.id[:8]} "{self.title}" [{self.priority}]>'

    def to_dict(self) -> dict:
        """
        Convert this model instance to a plain Python dict.

        Why not let the schema handle this?
        Because SQLAlchemy model instances are not plain dicts —
        they're ORM objects attached to a session. Marshmallow's
        dump() works on dicts and simple objects. to_dict() gives
        Marshmallow something clean and predictable to work with.
        """
        return {
            'id':         self.id,
            'title':      self.title,
            'done':       self.done,
            'priority':   self.priority,
            'created_at': self.created_at.isoformat() + 'Z' if self.created_at else None,
            'updated_at': self.updated_at.isoformat() + 'Z' if self.updated_at else None,
            'notes':      self.notes
        }