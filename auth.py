from authlib.integrations.requests_client import OAuth2Session
from flask import redirect, render_template, request, url_for, session, current_app, Blueprint

auth = Blueprint('auth', __name__, cli_group=None)
client = None


@auth.route("/oauth2_callback", methods=['GET'])
def oauth2_callback():
    if request.args.get('error'):
        current_app.logger.error('Error retrieving code: ' + request.args.get('error'))
        return 'Error'
    client = OAuth2Session(current_app.config['CLIENT_ID'], current_app.config['CLIENT_SECRET'], scope='accesslink.read_all')
    token_endpoint = 'https://polarremote.com/v2/oauth2/token'  # nosec
    session['token'] = client.fetch_token(token_endpoint, authorization_response=request.url)
    current_app.config.update(
        ACCESS_TOKEN=session['token']['access_token'],
        USER_ID=str(session['token']['x_user_id'])
    )
    current_app.logger.info('Acquired access token: ' + current_app.config['ACCESS_TOKEN'])
    return redirect(url_for('auth.index'))


@auth.route('/')
def index():
    if 'ACCESS_TOKEN' not in current_app.config:
        client = OAuth2Session(current_app.config['CLIENT_ID'], current_app.config['CLIENT_SECRET'], scope='accesslink.read_all')
        authorization_endpoint = 'https://flow.polar.com/oauth2/authorization'
        uri, state = client.create_authorization_url(authorization_endpoint)
        return render_template('index.html', uri=uri)
    return redirect(url_for('fetch.get_user_info', user_id=current_app.config['USER_ID']))
