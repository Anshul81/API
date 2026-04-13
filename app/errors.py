# app/errors.py

from flask import jsonify, g
from marshmallow import ValidationError
from app.exceptions import APIException


def register_error_handlers(app):

    # ── Custom APIException hierarchy ─────────────────────────
    @app.errorhandler(APIException)
    def handle_api_exception(err):
        """
        Catches every subclass of APIException.
        One handler covers NotFoundException, ForbiddenException, etc.
        """
        response = err.to_dict()
        response['correlation_id'] = g.get('correlation_id', '-')

        app.logger.warning(
            f"APIException: {err.code} — {err.message}"
        )
        return jsonify(response), err.status_code

    # ── Marshmallow validation errors ─────────────────────────
    @app.errorhandler(ValidationError)
    def handle_validation_error(err):
        app.logger.warning(f"ValidationError: {err.messages}")
        return jsonify({
            'error':          'Validation failed.',
            'code':           'VALIDATION_ERROR',
            'fields':         err.messages,
            'correlation_id': g.get('correlation_id', '-')
        }), 422

    # ── Standard HTTP errors ───────────────────────────────────
    @app.errorhandler(400)
    def bad_request(err):
        return jsonify({
            'error':          'Bad request.',
            'code':           'BAD_REQUEST',
            'correlation_id': g.get('correlation_id', '-')
        }), 400

    @app.errorhandler(404)
    def not_found(err):
        return jsonify({
            'error':          'The requested resource was not found.',
            'code':           'NOT_FOUND',
            'correlation_id': g.get('correlation_id', '-')
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(err):
        return jsonify({
            'error':          'HTTP method not allowed.',
            'code':           'METHOD_NOT_ALLOWED',
            'correlation_id': g.get('correlation_id', '-')
        }), 405

    # ── Catch-all for unexpected crashes ──────────────────────
    @app.errorhandler(Exception)
    def handle_unexpected_error(err):
        """
        This catches everything that nothing else caught —
        database crashes, null pointer errors, anything.

        We log the full traceback for developers but send
        a vague message to clients. Why vague? Because
        detailed error messages can leak internal information
        to attackers — stack traces, file paths, library versions.
        """
        app.logger.error(
            f"Unexpected error: {type(err).__name__}: {str(err)}",
            exc_info=True    # includes the full stack trace in the log
        )
        return jsonify({
            'error':          'An unexpected error occurred.',
            'code':           'INTERNAL_SERVER_ERROR',
            'correlation_id': g.get('correlation_id', '-')
        }), 500