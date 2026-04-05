from flask import jsonify
from marshmallow import ValidationError


def register_error_handlers(app):
    """
    Register global error handlers on the Flask app.
    Call this from the factory in app/__init__.py.

    These handlers catch errors thrown anywhere in the app —
    inside route handlers, before_request hooks, everywhere.
    """

    @app.errorhandler(ValidationError)
    def handle_validation_error(err):
        """
        Marshmallow raises ValidationError on schema.load() failure.
        This handler catches it globally so no route needs a try/except.

        err.messages is a dict like:
          {"title": ["Missing data for required field."]}
        """
        return jsonify({
            'error':  'Validation failed.',
            'code':   'VALIDATION_ERROR',
            'fields': err.messages      # per-field error details
        }), 422   # 422 Unprocessable Entity — data was received
                  # but failed semantic validation

    @app.errorhandler(400)
    def handle_bad_request(err):
        return jsonify({
            'error': 'Bad request. Ensure you are sending valid JSON.',
            'code':  'BAD_REQUEST'
        }), 400

    @app.errorhandler(404)
    def handle_not_found(err):
        return jsonify({
            'error': 'The requested resource was not found.',
            'code':  'NOT_FOUND'
        }), 404

    @app.errorhandler(405)
    def handle_method_not_allowed(err):
        return jsonify({
            'error': 'HTTP method not allowed on this endpoint.',
            'code':  'METHOD_NOT_ALLOWED'
        }), 405

    @app.errorhandler(500)
    def handle_internal_error(err):
        return jsonify({
            'error': 'An internal server error occurred.',
            'code':  'INTERNAL_SERVER_ERROR'
        }), 500