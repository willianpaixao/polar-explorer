import pytest

from app import create_app


def test_config():
    """Test create_app without passing test config."""
    assert create_app().testing


def test_empty_db(client):
    """Start with a blank database."""


if __name__ == '__main__':
    # Calling pytest directly instead of the CLI
    pytest.main()
