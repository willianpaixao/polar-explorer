import pytest


@pytest.fixture
def client():
    """ Creating an interface to mock a running application."""


def test_env(client):
    """ Make sure we're running the right environment."""


def test_empty_db(client):
    """Start with a blank database."""


if __name__ == '__main__':
    # Calling pytest directly instead of the CLI
    pytest.main()
