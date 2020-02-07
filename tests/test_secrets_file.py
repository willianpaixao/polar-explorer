def test_secrets_file(app):
    with app.app_context():
        assert 'CLIENT_ID' in app.config
        assert 'CLIENT_SECRET' in app.config
