import json

import click
from flask import Blueprint, current_app, jsonify, render_template, redirect, url_for
from requests import get, post, put
from requests.auth import AuthBase, HTTPBasicAuth

fetch = Blueprint('fetch', __name__, cli_group=None)


class BearerAuth(AuthBase):
    token = None

    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers['authorization'] = 'Bearer ' + self.token
        r.headers['accept'] = 'application/json'
        r.headers['content-type'] = 'application/json; charset=utf-8'
        return r


@fetch.route("/notifications")
def get_notifications():
    r = get(current_app.config['BASE_URL'] + '/v3/notifications', auth=HTTPBasicAuth(current_app.config['CLIENT_ID'], current_app.config['CLIENT_SECRET']))
    return jsonify(r.json())


@fetch.cli.command('fetch')
@click.option('-d', '--data', envvar='DATA_DIR', help='Directory to store the data')
@click.option('-t', '--token', required=True, envvar='ACCESS_TOKEN', help='OAuth2 Access Token.')
@click.option('-u', '--user-id', required=True, envvar='USER_ID', help='Polar user id.')
def fetch_command(token, user_id):
    get_activities_list(token=token, user_id=user_id)


@fetch.route("/users/<int:user_id>/activity-transactions")
def get_activities_list(token=None, user_id=None):
    """

    :param token: OAuth2 access token
    :param user_id: Polar user id
    """
    if not token:
        token = current_app.config['ACCESS_TOKEN']
    current_app.logger.debug("Starting an activity transaction")
    url = current_app.config['BASE_URL'] + '/v3/users/' + str(user_id) + '/activity-transactions'
    r = post(url=url, auth=BearerAuth(token=token))
    if r.status_code == 201:
        j = r.json()
        get_activities(token=token, user_id=user_id, transaction_id=j[u'transaction-id'])
        return redirect(url_for('fetch.get_notifications'))
    if r.status_code == 204:
        current_app.logger.info('No new data available')
        return redirect(url_for('fetch.get_notifications'))


def get_activities(token=None, user_id=None, transaction_id=None):
    """ Fetches all of available activity summaries

    Makes one call to the API, fetching a list of all available daily summaries
    then calls get_activity_summary() to effectively download the data.

    :param token: OAuth2 access token
    :param user_id: Polar user id
    :param transaction_id: The initiated transaction
    """
    if not token:
        token = current_app.config['ACCESS_TOKEN']
    url = current_app.config['BASE_URL'] + '/v3/users/' + str(user_id) + '/activity-transactions/' + str(transaction_id)
    r = get(url=url, auth=BearerAuth(token=token))
    if r.status_code == 200:
        j = r.json()
        for i in j[u'activity-log']:
            activity_id = i.split('/')[-1]
            r = get(current_app.config['BASE_URL'] + '/v3/users/' + str(user_id) + '/activity-transactions/' + str(transaction_id) + "/activities/" + str(activity_id), auth=BearerAuth(token=token))
            if r.status_code == 200:
                j = r.json()
                current_app.logger.info('Fetching activity summary of ' + j['date'])
                with open('daily-summary-' + str(j['id']) + '.json', 'w') as f:
                    json.dump(j, f, indent=2)
        current_app.logger.debug("Closing an activity transaction")
        r = put(url=url, auth=BearerAuth(token=token))
        if r.status_code == 200:
            current_app.logger.info("All activity information was successfully downloaded")
    elif r.status_code == 404:
        current_app.logger.error("Activity not found")
        return render_template('404.html')


@fetch.route("/users/<int:user_id>/exercise-transactions")
def get_exercise_list(token=None, user_id=None):
    """

    :param token: OAuth2 access token
    :param user_id: Polar user id
    """
    if not token:
        token = current_app.config['ACCESS_TOKEN']
    current_app.logger.debug("Starting an exercise transaction")
    url = current_app.config['BASE_URL'] + '/v3/users/' + str(user_id) + '/exercise-transactions'
    r = post(url=url, auth=BearerAuth(token=token))
    current_app.logger.error(r.status_code)
    if r.status_code == 201:
        return jsonify(r.json())
    elif r.status_code == 204:
        current_app.logger.info('No new data available')
        return render_template('204.html')


@fetch.route("/users/<int:user_id>/physical-information-transactions/<int:transaction_id>")
def list_user_physical_info(user_id, transaction_id):
    url = current_app.config['BASE_URL'] + '/v3/users/' + str(user_id) + '/physical-information-transactions/' + str(transaction_id)
    r = get(url=url, auth=BearerAuth(token=current_app.config['ACCESS_TOKEN']))
    if r.status_code == 200:
        j = r.json()
        for i in j[u'physical-informations']:
            s = get(url=i, auth=BearerAuth(token=current_app.config['ACCESS_TOKEN']))
            k = s.json()
            current_app.logger.info('Fetching physical information of ' + k['created'])
            with open('physical-information-' + str(k['id']) + '.json', 'w') as f:
                json.dump(k, f, indent=2)
        r = put(url=url, auth=BearerAuth(token=current_app.config['ACCESS_TOKEN']))
        current_app.logger.info(r.status_code)
        if r.status_code == 200:
            current_app.logger.info('All physical information was successfully downloaded')
            return redirect(url_for('fetch.get_notifications'))
    elif r.status_code == 204:
        current_app.logger.info('No new data available')
        return render_template('204.html')
    elif r.status_code == 404:
        return render_template('404.html')


@fetch.route("/users/<int:user_id>/physical-information-transactions")
def get_user_physical_info(user_id):
    """ Request physical information on the user

    :param user_id: Polar user id
    :return: User information in a JSON format
    """
    url = current_app.config['BASE_URL'] + '/v3/users/' + str(user_id) + '/physical-information-transactions'
    r = post(url=url, auth=BearerAuth(token=current_app.config['ACCESS_TOKEN']))
    if r.status_code == 201:
        j = r.json()
        return redirect(url_for('fetch.list_user_physical_info', user_id=user_id, transaction_id=j['transaction-id']))
    elif r.status_code == 204:
        current_app.logger.info('No new data available')
        return render_template('204.html')
    elif r.status_code == 404:
        return render_template('404.html')


@fetch.route("/users/<int:user_id>")
def get_user_info(user_id):
    """ Request profile information on the user

    :param user_id: Polar user id
    :return: User information in a JSON format
    """
    r = get(current_app.config['BASE_URL'] + '/v3/users/' + str(user_id), auth=BearerAuth(token=current_app.config['ACCESS_TOKEN']))
    if r.status_code == 200:
        return jsonify(r.json())
