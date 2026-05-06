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
    Login and activate session by switching into the organisation.
    Zedu requires an org switch after login to activate the session token.
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

    # Extract token from login response
    token = (
        login_data.get("data", {}).get("access_token")
        or login_data.get("access_token")
        or login_data.get("token")
        or login_data.get("data", {}).get("token")
    )
    if not token:
        raise ValueError(f"No token in login response: {login_data}")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Step 2: Try to switch org using slug to activate the session
    try:
        switch_response = requests.get(
            f"{BASE_URL}/users/switch-org/{ORG_SLUG}",
            headers=headers
        )
        if switch_response.status_code == 200:
            switch_data = switch_response.json()
            # Try to get a new token from the switch response
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
    except Exception:
        pass  # If switch fails, continue with original token

    # Step 3: Try switch-org using PUT /users/switch-org with body
    try:
        switch_response2 = requests.put(
            f"{BASE_URL}/users/switch-org",
            headers=headers,
            json={"organisation_id": ORG_SLUG}
        )
        if switch_response2.status_code == 200:
            switch_data2 = switch_response2.json()
            new_token2 = (
                switch_data2.get("data", {}).get("access_token")
                or switch_data2.get("access_token")
                or switch_data2.get("data", {}).get("token")
                or switch_data2.get("token")
            )
            if new_token2:
                token = new_token2
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
    except Exception:
        pass

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
    try:
        response = requests.get(
            f"{BASE_URL}/users/organisations",
            headers=auth_headers
        )
        if response.status_code == 200:
            data = response.json()
            orgs = data.get("data") or data
            if isinstance(orgs, list) and len(orgs) > 0:
                org = orgs[0]
                oid = org.get("id") or org.get("_id") or org.get("organisation_id")
                if oid:
                    return oid
    except Exception:
        pass
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