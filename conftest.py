import os
import uuid
import pytest
from dotenv import load_dotenv
from utils.auth import get_auth_token

load_dotenv()

BASE_URL = os.getenv("BASE_URL", "https://api.staging.zedu.chat/api/v1")


@pytest.fixture(scope="session")
def base_url():
    return BASE_URL


@pytest.fixture(scope="session")
def auth_token():
    return get_auth_token()


@pytest.fixture(scope="session")
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}


@pytest.fixture
def unique_email():
    return f"testuser_{uuid.uuid4().hex[:8]}@mailinator.com"


@pytest.fixture
def unique_username():
    return f"user_{uuid.uuid4().hex[:8]}"


@pytest.fixture(scope="session")
def registered_user_credentials():
    return {
        "email": os.getenv("TEST_EMAIL"),
        "password": os.getenv("TEST_PASSWORD"),
    }


@pytest.fixture(scope="session")
def wrong_password():
    return os.getenv("LOGIN_WRONG_PASSWORD", "WrongPassword999!")


@pytest.fixture(scope="session")
def bad_email():
    return os.getenv("LOGIN_BAD_EMAIL", "ghost_user@nowhere.com")