from flask import Flask, jsonify
from app.config import config_map, DevelopmentConfig
from app.errors import register_error_handlers      # ← new import


def create_app(config_name: str = 'development') -> Flask:
    app = Flask(__name__)

    config_class = config_map.get(config_name, DevelopmentConfig)
    app.config.from_object(config_class)

    # ── Register error handlers ───────────────────────
    register_error_handlers(app)                    # ← add this line

    # ── Register Blueprints ───────────────────────────
    from app.todos import todos_bp
    app.register_blueprint(todos_bp, url_prefix='/todos')

    @app.route('/ping')
    def ping():
        from datetime import datetime
        return jsonify({
            'status':    'ok',
            'version':   app.config['APP_VERSION'],
            'env':       app.config['ENV'],
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 200

    return app