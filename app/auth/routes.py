# app/auth/routes.py
from flask import jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)
from sqlalchemy import select

from app.auth import auth_bp
from app.auth.models import User
from app.auth.schemas import register_schema, login_schema, user_schema
from app.extensions import db



# ── REGISTER ──────────────────────────────────────────────────
@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Create a new user account.
    Password is hashed before saving — never stored in plain text.
    """
    raw_data = request.get_json()
    if not raw_data:
        return jsonify({'error': 'Request body must be JSON.',
                        'code': 'BAD_REQUEST'}), 400

    data = register_schema.load(raw_data)

    # Check if email already exists
    existing = db.session.execute(
        select(User).where(User.email == data['email'])
    ).scalar_one_or_none()

    if existing:
        return jsonify({
            'error': 'An account with this email already exists.',
            'code':  'CONFLICT'
        }), 409     # 409 Conflict — resource already exists

    user = User(email=data['email'], role=data.get('role', 'user'))
    user.set_password(data['password'])   # hashes + stores

    db.session.add(user)
    db.session.commit()

    return jsonify({
        'message': 'Account created successfully.',
        'user':    user_schema.dump(user.to_dict())
    }), 201


# ── LOGIN ─────────────────────────────────────────────────────
@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Verify credentials and return access + refresh tokens.

    We use the same vague error message whether the email
    doesn't exist OR the password is wrong. Why? If we said
    "email not found" an attacker learns which emails are
    registered. Vague errors prevent user enumeration attacks.
    """
    raw_data = request.get_json()
    if not raw_data:
        return jsonify({'error': 'Request body must be JSON.',
                        'code': 'BAD_REQUEST'}), 400

    data = login_schema.load(raw_data)

    user = db.session.execute(
        select(User).where(User.email == data['email'])
    ).scalar_one_or_none()

    # Same error whether email missing OR password wrong
    if not user or not user.check_password(data['password']):
        return jsonify({
            'error': 'Invalid email or password.',
            'code':  'UNAUTHORIZED'
        }), 401

    # additional_claims adds extra data into the JWT payload.
    # get_jwt() in protected routes reads this back out.
    access_token  = create_access_token(
        identity=user.id,
        additional_claims={'role': user.role, 'email': user.email}
    )
    refresh_token = create_refresh_token(
        identity=user.id,
        additional_claims={'role': user.role, 'email': user.email}
    )

    return jsonify({
        'access_token':  access_token,
        'refresh_token': refresh_token,
        'user':          user_schema.dump(user.to_dict())
    }), 200


# ── REFRESH ───────────────────────────────────────────────────
@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)    # only a refresh token is accepted here
def refresh():
    """
    Issue a new access token using the refresh token.
    The client calls this when the access token expires (401).
    """
    identity = get_jwt_identity()    # user ID from the token
    claims   = get_jwt()             # full payload including role

    new_access_token = create_access_token(
        identity=identity,
        additional_claims={'role': claims.get('role'), 'email': claims.get('email')}
    )

    return jsonify({'access_token': new_access_token}), 200


# ── ME ────────────────────────────────────────────────────────
@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    """
    Return the currently logged-in user's profile.
    get_jwt_identity() reads the 'sub' field from the token.
    """
    user_id = get_jwt_identity()
    user    = db.session.get(User, user_id)

    if not user:
        return jsonify({'error': 'User not found.', 'code': 'NOT_FOUND'}), 404

    return jsonify({'user': user_schema.dump(user.to_dict())}), 200