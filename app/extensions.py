from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
# Create extension instances without binding them to any app yet.
# The factory calls db.init_app(app) to bind them at runtime.
# This pattern is called "application-agnostic extensions."
db      = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()