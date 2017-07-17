import os
import pytest
from flask import Flask, url_for
from eventnotipy.database import db as _db
from eventnotipy.config import data

TESTDB = 'test_notify.db'
TESTDB_PATH = 'data/'
TEST_DATABASE_URI = 'sqlite:///' + TESTDB_PATH

@pytest.fixture
def app():
    settings_override = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': TEST_DATABASE_URI
    }

    app = Flask(__name__)
    app.config.update(settings_override)

    return app

def test_index(client):
    assert client.get(url_for('hello_world')).status_code == 200
