from marshmallow import Schema, fields, validate, validates, ValidationError, EXCLUDE


# ══════════════════════════════════════════
# TodoCreateSchema
# Used for POST /todos (creating a new todo)
# Only accepts fields the client is allowed to send.
# ══════════════════════════════════════════
class TodoCreateSchema(Schema):
    """
    Schema for validating the request body when creating a todo.

    'required=True' means Marshmallow raises ValidationError
    if the field is missing entirely from the request body.

    'load_default' sets the value if the field is absent
    (but not if it's present with a bad value).
    """
    title = fields.String(
        required=True,
        validate=[
            validate.Length(min=1, error="Title cannot be blank."),
            validate.Length(max=120, error="Title cannot exceed 120 characters."),
        ]
    )
    priority = fields.String(
        load_default='medium',      # default if not provided
        validate=validate.OneOf(
            ['low', 'medium', 'high'],
            error="Priority must be 'low', 'medium', or 'high'."
        )
    )

    class Meta:
        # EXCLUDE means unknown fields are silently ignored.
        # If a client sends {"title": "x", "hacked": true},
        # 'hacked' is stripped out — never reaches your route handler.
        # The alternative, RAISE, would return a 422 for unknown fields.
        unknown = EXCLUDE


# ══════════════════════════════════════════
# TodoUpdateSchema
# Used for PUT and PATCH /todos/<id>
# All fields are optional (for PATCH support).
# We validate only the fields that were actually sent.
# ══════════════════════════════════════════
class TodoUpdateSchema(Schema):
    """
    Schema for validating the request body when updating a todo.

    No field is required — PATCH only sends what changed.
    But if a field IS sent, it must still be valid.
    """
    title = fields.String(
        validate=[
            validate.Length(min=1, error="Title cannot be blank."),
            validate.Length(max=120, error="Title cannot exceed 120 characters."),
        ]
    )
    done     = fields.Boolean()
    priority = fields.String(
        validate=validate.OneOf(
            ['low', 'medium', 'high'],
            error="Priority must be 'low', 'medium', or 'high'."
        )
    )

    class Meta:
        unknown = EXCLUDE

    @validates('title')
    def validate_title_not_whitespace(self, value):
        """
        Custom validator — Marshmallow calls this automatically
        after the field-level validators pass.

        validate.Length(min=1) passes for a single space " ".
        This catches that edge case.
        """
        if not value.strip():
            raise ValidationError("Title cannot be blank or only whitespace.")


# ══════════════════════════════════════════
# TodoSchema
# Used for serialising todos on the way OUT.
# Controls exactly what fields the client sees.
# ══════════════════════════════════════════
class TodoSchema(Schema):
    """
    Full todo schema for serialising response data.

    dump_only=True means:
      - The field appears in schema.dump() output (responses)
      - The field is IGNORED in schema.load() input (requests)

    This prevents clients from ever setting id, created_at,
    or updated_at — the server always controls those.
    """
    id         = fields.String(dump_only=True)
    title      = fields.String()
    done       = fields.Boolean()
    priority   = fields.String()
    created_at = fields.String(dump_only=True)
    updated_at = fields.String(dump_only=True)


# ══════════════════════════════════════════
# Module-level schema instances
# Instantiate once, reuse everywhere.
# Schema instantiation is not free — don't
# create new instances inside route handlers.
# ══════════════════════════════════════════
todo_schema        = TodoSchema()           # single todo
todos_schema       = TodoSchema(many=True)  # list of todos
todo_create_schema = TodoCreateSchema()
todo_update_schema = TodoUpdateSchema()