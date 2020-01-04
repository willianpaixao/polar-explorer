import os
import sys

from authlib.integrations.requests_client import OAuth2Session
from flask import Flask, redirect, render_template, request, url_for, session

client = None


def create_app():
    app = Flask(__name__)

    if app.config['ENV'] == 'development':
        app.config.from_object('default.DevelopmentConfig')
        if 'SECRETS_FILE' not in os.environ:
            app.logger.error("Secret file not provided, aborting...")
            sys.exit()
        try:
            app.config.from_envvar('SECRETS_FILE')
        except SyntaxError:
            app.logger.error("Invalid secret file '%s', aborting...", os.environ['SECRETS_FILE'])
            sys.exit()
        app.logger.info("Configuration loaded successfully")
    if app.config['ENV'] == 'testing':
        app.config.from_object('default.TestingConfig')

    from fetch import fetch
    app.register_blueprint(fetch)

    return app


app = create_app()


@app.route("/oauth2_callback", methods=['GET'])
def oauth2_callback():
    global client
    if request.args.get('error'):
        app.logger.error('Error retrieving code: ' + request.args.get('error'))
        return 'Error'
    token_endpoint = 'https://polarremote.com/v2/oauth2/token'
    session['token'] = client.fetch_token(token_endpoint, authorization_response=request.url)
    app.config.update(
        ACCESS_TOKEN=session['token']['access_token'],
        USER_ID=str(session['token']['x_user_id'])
    )
    app.logger.info('Acquired access token: ' + app.config['ACCESS_TOKEN'])
    return redirect(url_for('index'))


@app.route('/')
def index():
    if app.config['ENV'] == 'testing':
        return 'Hello, World!'
    if 'ACCESS_TOKEN' not in app.config:
        global client
        client = OAuth2Session(app.config['CLIENT_ID'], app.config['CLIENT_SECRET'], scope='accesslink.read_all')
        authorization_endpoint = 'https://flow.polar.com/oauth2/authorization'
        uri, state = client.create_authorization_url(authorization_endpoint)
        return render_template('index.html', uri=uri)
    return redirect(url_for('fetch.get_user_info', user_id=session['token']['x_user_id']))


if __name__ == '__main__':
    app.run()
