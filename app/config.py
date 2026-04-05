import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'change_in_production')
    APP_VERSION = os.environ.get('APP_VERSION', '1.0.0')
    APP_NAME = 'Flask API Course'

    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    """
    Used when running locally: debug on, verbose logging.
    Flask reloads automatically when you save a file.
    """
    DEBUG   = True
    TESTING = False
    ENV     = 'development'


class ProductionConfig(Config):
    """
    Used on a real server. Debug MUST be False — debug mode
    exposes an interactive Python shell in the browser on errors.
    That's a catastrophic security hole in production.
    """
    DEBUG   = False
    TESTING = False
    ENV     = 'production'


class TestingConfig(Config):
    """
    Used by pytest in Chapter 12.
    Separate DB, no real secret keys, fast bcrypt rounds.
    """
    DEBUG   = False
    TESTING = True
    ENV     = 'testing'


# Map string names to config classes.
# The app factory uses this dict to look up the right class.
config_map = {
    'development': DevelopmentConfig,
    'production':  ProductionConfig,
    'testing':     TestingConfig,
}