import os
import uuid
import pytest
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL", "https://api.zedu.chat/api/v1")
ORG_SLUG = os.getenv("TEST_ORG_ID", "zedu-test-organisation")
ORG_ID = "019de302-9c35-7a83-9c72-177d901cd4c1"


def get_fresh_headers():
    """
    Get fresh authenticated headers every time.
    Zedu tokens expire quickly so we refresh per test class.
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
    token = login_response.json()["data"]["access_token"]

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "org-id": ORG_ID,
    }

    # Step 2: Switch org to activate session
    switch_response = requests.get(
        f"{BASE_URL}/users/switch-org/{ORG_SLUG}",
        headers=headers
    )
    if switch_response.status_code == 200:
        activated_token = switch_response.json()["data"]["access_token"]
        if activated_token:
            headers["Authorization"] = f"Bearer {activated_token}"

    return headers


@pytest.fixture(scope="session")
def base_url():
    return BASE_URL


@pytest.fixture(scope="session")
def org_slug():
    return ORG_SLUG


@pytest.fixture(scope="session")
def org_id():
    return ORG_ID


# Use "module" scope so token refreshes per test file
@pytest.fixture(scope="module")
def auth_headers():
    return get_fresh_headers()


@pytest.fixture(scope="module")
def auth_token(auth_headers):
    return auth_headers["Authorization"].replace("Bearer ", "")


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