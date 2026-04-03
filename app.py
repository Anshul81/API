import os
from datetime import datetime
from flask import Flask, jsonify
from dotenv import load_dotenv

# Load environment variables from .env into os.environ
load_dotenv()

# Create the Flask application instance
# __name__ tells Flask where to find resources relative to this file
app = Flask(__name__)

# Load config from environment variables
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback-secret')
app.config['VERSION'] = os.getenv('APP_VERSION', '1.0.0')


# ──────────────────────────────────────────
# ENDPOINT 1: Health check
# GET /ping
# ──────────────────────────────────────────
@app.route('/ping', methods=['GET'])
def ping():
    """
    Health check endpoint.
    Load balancers and monitoring tools call this to verify
    the service is alive. Always returns 200 if the app is running.
    """
    return jsonify({
        'status': 'ok',
        'message': 'pong',
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }), 200


# ──────────────────────────────────────────
# ENDPOINT 2: Personalised greeting
# GET /hello/<name>
# ──────────────────────────────────────────
@app.route('/hello/<string:name>', methods=['GET'])
def hello(name):
    """
    Greet a user by name.
    <string:name> is a URL parameter — Flask extracts it and
    passes it as an argument to this function.
    """
    # Basic sanitisation — reject names that are too long
    if len(name) > 50:
        return jsonify({
            'error': 'Name is too long. Max 50 characters.',
            'code': 'VALIDATION_ERROR'
        }), 400  # 400 = Bad Request — the client sent invalid data

    return jsonify({
        'message': f'Hello, {name}!',
        'name': name,
        'greeted_at': datetime.utcnow().isoformat() + 'Z'
    }), 200


# ──────────────────────────────────────────
# ENDPOINT 3: Server info
# GET /info
# ──────────────────────────────────────────
@app.route('/info', methods=['GET'])
def info():
    """
    Returns metadata about this API.
    Useful for clients to discover what version they're talking to.
    """
    return jsonify({
        'api': 'Flask API Course',
        'version': app.config['VERSION'],
        'environment': os.getenv('FLASK_ENV', 'production'),
        'endpoints': [
            {'method': 'GET', 'path': '/ping',         'description': 'Health check'},
            {'method': 'GET', 'path': '/hello/<name>', 'description': 'Greet a user'},
            {'method': 'GET', 'path': '/info',         'description': 'API information'},
        ]
    }), 200


@app.route("/hello", methods=["GET"])
def hello_simple():
    return jsonify({"message": "Take Care!"}), 400
# ──────────────────────────────────────────
# Run the development server
# ──────────────────────────────────────────
if __name__ == '__main__':
    # debug=True enables:
    #  - Auto-reload when you save the file
    #  - Detailed error pages in the browser
    # NEVER use debug=True in production
    app.run(debug=True, host='0.0.0.0', port=5000)