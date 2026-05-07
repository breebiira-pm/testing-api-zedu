import os
import uuid
import pytest
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL", "https://api.zedu.chat/api/v1")
ORG_SLUG = os.getenv("TEST_ORG_ID", "zedu-test-organisation")


def login_and_activate_session():
    """
    Two-step Zedu authentication:
    1. POST /auth/login — returns initial token
    2. GET /users/switch-org/{slug} — returns activated session token
    The second token is what works for all protected endpoints.
    """
    # Step 1: Login
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": os.getenv("TEST_EMAIL"),
            "password": os.getenv("TEST_PASSWORD"),
        }
    )
    login_response.raise_for_status()
    login_data = login_response.json()

    # Token is inside data.access_token
    token = login_data["data"]["access_token"]

    if not token:
        raise ValueError(f"No token in login response: {login_data}")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Step 2: Switch org to get activated session token
    switch_response = requests.get(
        f"{BASE_URL}/users/switch-org/{ORG_SLUG}",
        headers=headers
    )

    if switch_response.status_code == 200:
        switch_data = switch_response.json()
        # New activated token is inside data.access_token
        activated_token = switch_data["data"]["access_token"]
        if activated_token:
            headers = {
                "Authorization": f"Bearer {activated_token}",
                "Content-Type": "application/json"
            }

    return headers


@pytest.fixture(scope="session")
def base_url():
    return BASE_URL


@pytest.fixture(scope="session")
def org_slug():
    return ORG_SLUG


@pytest.fixture(scope="session")
def auth_headers():
    return login_and_activate_session()


@pytest.fixture(scope="session")
def auth_token(auth_headers):
    return auth_headers["Authorization"].replace("Bearer ", "")


@pytest.fixture(scope="session")
def org_id():
    return "019de302-9c35-7a83-9c72-177d901cd4c1"


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