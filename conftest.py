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
    Login and then switch into the organisation to get a valid session token.
    Zedu requires switching org after login to activate the session.
    """
    # Step 1: Login
    login_url = f"{BASE_URL}/auth/login"
    payload = {
        "email": os.getenv("TEST_EMAIL"),
        "password": os.getenv("TEST_PASSWORD"),
    }
    response = requests.post(login_url, json=payload)
    response.raise_for_status()
    data = response.json()

    token = (
        data.get("data", {}).get("access_token")
        or data.get("access_token")
        or data.get("token")
        or data.get("data", {}).get("token")
    )
    if not token:
        raise ValueError(f"Could not extract token from login response: {data}")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Step 2: Switch into the organisation using slug to activate session
    switch_url = f"{BASE_URL}/users/switch-org/{ORG_SLUG}"
    switch_response = requests.get(switch_url, headers=headers)

    # If switch gives us a new token, use that
    if switch_response.status_code == 200:
        switch_data = switch_response.json()
        new_token = (
            switch_data.get("data", {}).get("access_token")
            or switch_data.get("access_token")
            or switch_data.get("data", {}).get("token")
            or switch_data.get("token")
        )
        if new_token:
            token = new_token
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }

    return token, headers


@pytest.fixture(scope="session")
def base_url():
    return BASE_URL


@pytest.fixture(scope="session")
def org_slug():
    return ORG_SLUG


@pytest.fixture(scope="session")
def auth_token():
    token, _ = login_and_activate_session()
    return token


@pytest.fixture(scope="session")
def auth_headers():
    _, headers = login_and_activate_session()
    return headers


@pytest.fixture(scope="session")
def org_id(auth_headers):
    """Get the real org UUID from the organisations list."""
    response = requests.get(f"{BASE_URL}/users/organisations", headers=auth_headers)
    if response.status_code == 200:
        data = response.json()
        orgs = data.get("data") or data
        if isinstance(orgs, list) and len(orgs) > 0:
            org = orgs[0]
            oid = org.get("id") or org.get("_id") or org.get("organisation_id")
            if oid:
                return oid
    return ORG_SLUG


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