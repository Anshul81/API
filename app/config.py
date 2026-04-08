import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY    = os.getenv('SECRET_KEY', 'change-me-in-production')
    APP_VERSION   = os.getenv('APP_VERSION', '1.0.0')
    APP_NAME      = 'Flask API Course'
    SQLALCHEMY_TRACK_MODIFICATIONS = False   # suppress a noisy warning


class DevelopmentConfig(Config):
    DEBUG   = True
    TESTING = False
    ENV     = 'development'

    # SQLite — a single file in the project root.
    # No server needed, perfect for local dev.
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'sqlite:///todos_dev.db'          # file: instance/todos_dev.db
    )
    # Echo SQL to console — invaluable for debugging.
    # You'll see the exact SQL Flask-SQLAlchemy generates.
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    DEBUG   = False
    TESTING = False
    ENV     = 'production'

    # PostgreSQL — must be set as an env var in production.
    # Never hardcode credentials.
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_ECHO = False


class TestingConfig(Config):
    DEBUG   = False
    TESTING = True
    ENV     = 'testing'

    # Separate in-memory SQLite for tests.
    # Each test run starts with a blank database —
    # tests never interfere with your dev data.
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_ECHO = False


config_map = {
    'development': DevelopmentConfig,
    'production':  ProductionConfig,
    'testing':     TestingConfig,
}