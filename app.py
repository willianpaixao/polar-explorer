import logging
import os

from flask import Flask


def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    if test_config is None:
        configure_app(app)
    else:
        app.config.update(test_config)

    from fetch import fetch
    app.register_blueprint(fetch)
    from auth import auth
    app.register_blueprint(auth)

    return app


def configure_app(app):
    """  Loads a different set of configurations depending on the desired environment

    :param app: Flask app instance
    """
    if app.config['ENV'] == 'development':
        app.config.from_object('config.DevelopmentConfig')
    if app.config['ENV'] == 'testing':
        app.config.from_object('config.TestingConfig')

    if 'SECRETS_FILE' in os.environ:
        try:
            app.config.from_envvar('SECRETS_FILE')
        except SyntaxError:
            app.logger.error("Invalid secret file '{}', aborting...", os.environ['SECRETS_FILE'])
    else:
        app.logger.error("Secret file not provided, aborting...")

    app.logger.info("Configuration loaded successfully")

    logging.getLogger("urllib3").setLevel(logging.WARNING)
