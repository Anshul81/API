# app/exceptions.py


class APIException(Exception):
    """
    Base class for all custom API exceptions.

    Every exception in your app inherits from this.
    The global error handler catches this one class
    and handles every subclass automatically.

    Why classes instead of just returning jsonify() directly?
    Because exceptions can be RAISED from anywhere —
    deep inside a helper function, inside a model method,
    inside a utility function. You don't need to pass
    a response object around. Just raise the exception
    and the global handler catches it.
    """
    status_code = 500
    code        = 'INTERNAL_SERVER_ERROR'
    message     = 'An unexpected error occurred.'

    def __init__(self, message=None, code=None, status_code=None):
        # Allow overriding defaults at raise time:
        # raise NotFoundException("Todo not found")
        if message:
            self.message     = message
        if code:
            self.code        = code
        if status_code:
            self.status_code = status_code
        super().__init__(self.message)

    def to_dict(self):
        """Serialise to a dict — used by the error handler."""
        return {
            'error': self.message,
            'code':  self.code,
        }


# ── Specific exception classes ────────────────────────────────
# Each one is a single line — they inherit everything from
# APIException and just override the defaults.

class NotFoundException(APIException):
    """Raise when a requested resource does not exist."""
    status_code = 404
    code        = 'NOT_FOUND'
    message     = 'The requested resource was not found.'


class ValidationException(APIException):
    """Raise when incoming data fails business logic validation."""
    status_code = 422
    code        = 'VALIDATION_ERROR'
    message     = 'Validation failed.'


class AuthenticationException(APIException):
    """Raise when credentials are missing or invalid."""
    status_code = 401
    code        = 'UNAUTHORIZED'
    message     = 'Authentication required.'


class ForbiddenException(APIException):
    """Raise when a user is authenticated but lacks permission."""
    status_code = 403
    code        = 'FORBIDDEN'
    message     = 'You do not have permission to perform this action.'


class ConflictException(APIException):
    """Raise when a resource already exists."""
    status_code = 409
    code        = 'CONFLICT'
    message     = 'A conflict occurred with the current state of the resource.'