import pytest

import app
import db


@pytest.fixture
def client():
    """ Creating an interface to mock a running application."""
    with app.app.test_client() as client:
        with app.app.app_context():
            db.init_db()
        yield client


def test_env(client):
    """ Make sure we're running the right environment."""
    assert 'testing' == app.app.config['ENV']


def test_empty_db(client):
    """Start with a blank database."""

    r = client.get('/')
    assert b'Hello, World!' in r.data


if __name__ == '__main__':
    # Calling pytest directly instead of the CLI
    pytest.main()
