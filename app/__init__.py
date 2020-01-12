import logging
import os
import sys

from flask import Flask


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    configure_app(app)

    from .fetch import fetch
    app.register_blueprint(fetch)
    from .auth import auth
    app.register_blueprint(auth)

    return app


def configure_app(app):
    """  Loads a different set of configurations depending on the desired environment

    :param app: Flask app instance
    """
    if app.config['ENV'] == 'development':
        app.config.from_object('config.DevelopmentConfig')
        if 'SECRETS_FILE' not in os.environ:
            app.logger.error("Secret file not provided, aborting...")
            sys.exit()
        try:
            app.config.from_envvar('SECRETS_FILE')
        except SyntaxError:
            app.logger.error("Invalid secret file '{}', aborting...", os.environ['SECRETS_FILE'])
            sys.exit()
        app.logger.info("Configuration loaded successfully")
    if app.config['ENV'] == 'testing':
        app.config.from_object('config.TestingConfig')

    logging.getLogger("urllib3").setLevel(logging.WARNING)
