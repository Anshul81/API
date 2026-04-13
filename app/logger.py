# app/logger.py

import logging
import sys


def configure_logging(app):
    """
    Configure structured logging for the Flask app.

    We set up one handler that writes to stdout (the terminal).
    In production, stdout gets captured by your container/server
    and forwarded to a log aggregator like Datadog or CloudWatch.
    """

    # Remove Flask's default handlers so we control the format
    app.logger.handlers.clear()

    # Create a handler that writes to stdout
    handler = logging.StreamHandler(sys.stdout)

    # Format: timestamp | level | correlation_id | message
    # The correlation_id comes from the request context (Step 4)
    formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(correlation_id)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)

    # Set log level based on environment
    log_level = logging.DEBUG if app.config.get('DEBUG') else logging.INFO
    handler.setLevel(log_level)
    app.logger.setLevel(log_level)
    app.logger.addHandler(handler)

    # Suppress noisy SQLAlchemy logs in production
    if not app.config.get('DEBUG'):
        logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)