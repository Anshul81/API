from flask_marshmallow import validate
from marshmallow import Schema, fields, EXCLUDE, validate


class RegisterSchema(Schema):

    email = fields.Email(
        required=True,
        error_messages={'required': 'Email is required'}
    )

    password = fields.String(
        required=True,
        validate=validate.Length(
            min=8,
            error='Password must be at least 8 characters long.'
        ),
        # Skip this field during serialization
        load_only=True
    )

    role = fields.String(
        load_default='user',
        validate=validate.OneOf(['user', 'admin'],error='Role must be one of user or admin')
    )


    class Meta:
        unknown = EXCLUDE


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True, load_only=True)

    class Meta:
        unknown = EXCLUDE


class UserSchema(Schema):

    id = fields.String(dump_only=True)
    email = fields.Email(dump_only=True)
    role = fields.String(dump_only=True)
    created_at = fields.String(dump_only=True)

register_schema = RegisterSchema()
login_schema = LoginSchema()
user_schema = UserSchema()