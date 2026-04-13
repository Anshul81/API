# app/middleware.py

import uuid
import time
import logging
from flask import request, g


# ── Logging filter — injects correlation_id into every log line ──
class CorrelationIdFilter(logging.Filter):
    """
    A logging filter that adds correlation_id to every log record.

    Python's logging module calls filter() on every log record
    before writing it. We inject the correlation_id from Flask's
    request context (g.correlation_id) so it appears in every
    log line automatically — you never have to pass it manually.

    If there's no active request (e.g. during startup), we use '-'.
    """
    def filter(self, record):
        try:
            record.correlation_id = g.get('correlation_id', '-')
        except RuntimeError:
            # RuntimeError means we're outside a request context
            record.correlation_id = '-'
        return True


def register_middleware(app):
    """
    Register before_request and after_request hooks.
    Called from the app factory.
    """

    # Attach the correlation ID filter to the app logger
    app.logger.addFilter(CorrelationIdFilter())

    # ── BEFORE every request ──────────────────────────────────
    @app.before_request
    def before_request():
        """
        Runs before EVERY request, before any route handler.

        We do three things here:
        1. Generate a unique correlation ID for this request
        2. Store it in Flask's 'g' object (request-scoped storage)
        3. Record the start time so we can calculate duration
        """
        # Check if client sent their own correlation ID
        # (useful when services call each other — they can pass
        # the same ID through so logs across services are linked)
        correlation_id = request.headers.get(
            'X-Correlation-ID',
            str(uuid.uuid4())      # generate one if client didn't send it
        )

        # g is Flask's request context storage.
        # It lives for exactly one request — created before_request,
        # destroyed after_request. Perfect for per-request data.
        g.correlation_id = correlation_id
        g.start_time     = time.time()

        app.logger.info(
            f"→ {request.method} {request.path} "
            f"| ip={request.remote_addr} "
            f"| agent={request.user_agent.string[:50]}"
        )

    # ── AFTER every request ───────────────────────────────────
    @app.after_request
    def after_request(response):
        """
        Runs after EVERY request, after the route handler.

        We do three things here:
        1. Calculate request duration
        2. Add correlation ID to the response headers
           (so clients can reference it in bug reports)
        3. Log the completed request with status + duration
        """
        duration = time.time() - g.get('start_time', time.time())
        duration_ms = round(duration * 1000, 2)

        # Add correlation ID to response so the client
        # can quote it when reporting a problem
        response.headers['X-Correlation-ID'] = g.get('correlation_id', '-')

        # Log level based on status code
        # 5xx errors are ERROR level, 4xx are WARNING, rest are INFO
        status = response.status_code
        if status >= 500:
            log_fn = app.logger.error
        elif status >= 400:
            log_fn = app.logger.warning
        else:
            log_fn = app.logger.info

        log_fn(
            f"← {request.method} {request.path} "
            f"| status={status} "
            f"| duration={duration_ms}ms"
        )

        return response