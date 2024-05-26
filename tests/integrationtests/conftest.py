import pytest
from tests import APP, DATABASE
from tests.utils import tear_down_database


@pytest.fixture
def client():

    # Create and apply migrations to the test database
    with APP.app_context():
        DATABASE.create_all()
        client = APP.test_client()

        yield client
        tear_down_database()
