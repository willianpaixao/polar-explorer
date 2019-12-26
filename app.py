import os
import sys

from authlib.integrations.requests_client import OAuth2Session
from flask import Flask
from flask import jsonify, request
from requests import get, post
from requests.auth import AuthBase, HTTPBasicAuth

baseUrl = None
client = None
token = None


def create_app():
    global app
    app = Flask(__name__)
    with app.app_context():
        import db
        db.init_app(app)
    if app.config['ENV'] == 'development':
        app.config.from_object('default.DevelopmentConfig')
        if not os.environ['SECRETS_FILE']:
            app.logger.error("Secret file not provided, aborting...")
            sys.exit()
        try:
            app.config.from_envvar('SECRETS_FILE')
        except SyntaxError:
            app.logger.error("Invalid secret file '%s', aborting...", os.environ['SECRETS_FILE'])
            sys.exit()
        global baseUrl
        baseUrl = app.config['BASE_URL']
        app.logger.info("Configuration loaded successfully")
    if app.config['ENV'] == 'testing':
        app.config.from_object('default.TestingConfig')
    return app


app = create_app()


class BearerAuth(AuthBase):
    token = None

    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers["authorization"] = "Bearer " + self.token
        return r


@app.route("/notifications")
def get_notifications():
    r = get(baseUrl + '/v3/notifications', auth=HTTPBasicAuth(app.config['CLIENT_ID'], app.config['CLIENT_SECRET']))
    return jsonify(r.json())


@app.route("/oauth2_callback", methods=['GET'])
def oauth2_callback():
    global token
    if request.args.get('error'):
        app.logger.error('Error retrieving code: ' + request.args.get('error'))
        return 'Error'
    token_endpoint = 'https://polarremote.com/v2/oauth2/token'
    t = client.fetch_token(token_endpoint, authorization_response=request.url)
    token = t['access_token']
    app.logger.info('Access token: ' + token)
    return 'Authorized!'


@app.route("/users/<user_id>/activity-transactions/<transaction_id>/activities/<activity_id>/step-samples")
def get_step_samples(user_id=None, transaction_id=None, activity_id=None):
    r = get(baseUrl + '/v3/users/' + user_id + '/activity-transactions/' + transaction_id + "/activities/" + activity_id + "/step-samples", auth=BearerAuth(token=token))
    app.logger.debug(r.json())
    if r.status_code == 200:
        return jsonify(r.json())
    if r.status_code == 204:
        return 'No new data available'


@app.route("/users/<user_id>")
def get_user_info(user_id=None):
    r = get(baseUrl + '/v3/users/' + user_id, auth=BearerAuth(token=token))
    if r.status_code == 200:
        return r.text


@app.route('/')
def hello_world():
    if app.config['ENV'] == 'testing':
        return 'Hello, World!'
    global client
    client = OAuth2Session(app.config['CLIENT_ID'], app.config['CLIENT_SECRET'], scope='accesslink.read_all')
    authorization_endpoint = 'https://flow.polar.com/oauth2/authorization'
    uri, state = client.create_authorization_url(authorization_endpoint)
    app.logger.debug(uri)
    return 'Hello, World!'


if __name__ == '__main__':
    app.run()
