from datetime import datetime

import bcrypt

from app.extensions import db
import uuid

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.String(36), primary_key=True,
                   default=lambda: str(uuid.uuid4()))

    email = db.Column(db.String(120), unique=True, nullable=False,
                      index=True)

    password_hash = db.Column(db.String(128), nullable=False)

    role = db.Column(db.String(20), nullable=False, default = 'user')

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'User {self.email} [{self.role}]'

    def set_password(self, raw_password: str):
        # Encode is used because bcrypt needs bytes type not a string
        hashed = bcrypt.hashpw(raw_password.encode('utf-8'), bcrypt.gensalt(rounds=12))
        # Decode is used to save the password as a string in DB.
        self.password_hash = hashed.decode('utf-8')

    def check_password(self, raw_password: str) -> bool:
        """
                Verify a raw password against the stored hash.

                bcrypt extracts the salt from the stored hash automatically
                and re-hashes the raw password with it. If the results match,
                the password is correct — without ever decoding the hash.
                """
        return bcrypt.checkpw(raw_password.encode('utf-8'),
                              self.password_hash.encode('utf-8'))


    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat() + 'Z'
        }