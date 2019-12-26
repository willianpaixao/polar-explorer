import json
import logging

import click
from requests import post, get
from requests.auth import AuthBase

BASE_URL = 'https://www.polaraccesslink.com'
logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s', level=logging.DEBUG)
logger = logging.getLogger('fetch')
logging.getLogger("urllib3").setLevel(logging.WARNING)


class BearerAuth(AuthBase):
    token = None

    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers["authorization"] = "Bearer " + self.token
        return r


@click.command()
@click.option('-d', '--data', envvar='DATA_DIR', help='Directory to store the data')
@click.option('-t', '--token', required=True, envvar='ACCESS_TOKEN', help='OAuth2 Access Token.')
@click.option('-u', '--user-id', required=True, envvar='USER_ID', help='Polar user id.')
def fetch_command(token, user_id, data=None):
    fetch(token=token, user_id=user_id)


def fetch(token=None, user_id=None):
    """

    :param token: OAuth2 access token
    :param user_id: Polar user id
    """
    r = post(BASE_URL + '/v3/users/' + user_id + '/activity-transactions', auth=BearerAuth(token=token))
    if r.status_code == 201:
        j = r.json()
        get_activities(token=token, user_id=user_id, transaction_id=str(j[u'transaction-id']))
    if r.status_code == 204:
        logger.info('No new data available')


def get_activities(token=None, user_id=None, transaction_id=None):
    """ Fetches all of available activity summaries

    Makes one call to the API, fetching a list of all available daily summaries
    then calls get_activity_summary() to effectively download the data.

    :param token: OAuth2 access token
    :param user_id: Polar user id
    :param transaction_id: The initiated transaction
    """
    r = get(BASE_URL + '/v3/users/' + user_id + '/activity-transactions/' + transaction_id, auth=BearerAuth(token=token))
    if r.status_code == 200:
        j = r.json()
        for i in j[u'activity-log']:
            activity_id = i.split('/')[-1]
            get_activity_summary(token=token, user_id=user_id, transaction_id=transaction_id, activity_id=activity_id)
    if r.status_code == 404:
        logger.error("Activity not found")


def get_activity_summary(token=None, user_id=None, transaction_id=None, activity_id=None):
    """ Download one daily activity summary

    :param token: OAuth2 access token
    :param user_id: Polar user id
    :param transaction_id: The initiated transaction
    :param activity_id: Summary to be downloaded
    """
    r = get(BASE_URL + '/v3/users/' + user_id + '/activity-transactions/' + transaction_id + "/activities/" + activity_id, auth=BearerAuth(token=token))
    if r.status_code == 200:
        j = r.json()
        logger.info('Fetching activity summary of ' + j['date'] + '...')
        with open('daily-summary-' + str(j['id']) + '.json', 'w') as f:
            json.dump(j, f, indent=2)


if __name__ == '__main__':
    fetch_command()
