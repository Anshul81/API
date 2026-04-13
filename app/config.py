import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY    = os.getenv('SECRET_KEY', 'change-me-in-production')
    APP_VERSION   = os.getenv('APP_VERSION', '1.0.0')
    APP_NAME      = 'Flask API Course'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ── JWT settings ──────────────────────────────────
    # The key used to sign every token.
    # If this leaks, anyone can forge tokens — keep it secret.
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-change-me')

    # Access token: short-lived — limits damage if stolen.
    # If a token is stolen, it only works for 15 minutes.
    JWT_ACCESS_TOKEN_EXPIRES  = timedelta(minutes=15)

    # Refresh token: long-lived — used only to get new access tokens.
    # User stays logged in for 7 days without re-entering password.
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False
    ENV   = 'development'
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///todos_dev.db')
    SQLALCHEMY_ECHO = True

    # Longer expiry in dev so you're not constantly re-logging in
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    ENV   = 'production'
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_ECHO = False


class TestingConfig(Config):
    DEBUG   = False
    TESTING = True
    ENV     = 'testing'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=5)  # expire fast in tests


config_map = {
    'development': DevelopmentConfig,
    'production':  ProductionConfig,
    'testing':     TestingConfig,
}