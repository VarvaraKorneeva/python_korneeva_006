from flask_006 import __version__
from flask_006.flaskapp import app


def test_version():
    assert __version__ == '0.1.0'


def test_index_is_ok():
    app.testing = True
    client = app.test_client()

    response = client.get('/')
    assert response == 200
