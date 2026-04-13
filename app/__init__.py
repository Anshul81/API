import os
from flask import Flask, jsonify
from app.config import config_map, DevelopmentConfig
from app.errors import register_error_handlers
from app.extensions import db, migrate, jwt


def create_app(config_name: str = 'development') -> Flask:
    app = Flask(__name__)

    # ── Config ────────────────────────────────────────
    config_class = config_map.get(config_name, DevelopmentConfig)
    app.config.from_object(config_class)

    # ── Initialise extensions ─────────────────────────
    # init_app() binds the extension to this specific app instance.
    # This is what makes the factory pattern work — same db object,
    # different app instances (dev app, test app, prod app).
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # ── Error handlers ────────────────────────────────
    register_error_handlers(app)

    # ── Blueprints ────────────────────────────────────
    from app.todos import todos_bp
    app.register_blueprint(todos_bp, url_prefix='/todos')

    from app.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # ── Health check ──────────────────────────────────
    @app.route('/ping')
    def ping():
        from datetime import datetime
        # Also check DB connectivity in the health check
        try:
            db.session.execute(db.text('SELECT 1'))
            db_status = 'ok'
        except Exception:
            db_status = 'error'

        return jsonify({
            'status':    'ok',
            'db':        db_status,
            'version':   app.config['APP_VERSION'],
            'env':       app.config['ENV'],
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 200

    return app