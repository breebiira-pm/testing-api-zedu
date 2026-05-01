"""
test_users.py
=============
Tests for the Zedu user endpoints:
  - GET  /users/me
  - GET  /users/{userId}
  - PUT  /users/{userId}
  - GET  /users/organisations
  - GET  /users/notification-preferences
  - PUT  /users/notification-preferences

Covers: positive, negative, and edge case scenarios.
"""

import os
import uuid
import pytest
import requests
from dotenv import load_dotenv

load_dotenv()


# ──────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────

def get_current_user_id(base_url, auth_headers):
    """Helper: fetch the current user's ID via /users/me."""
    response = requests.get(f"{base_url}/users/me", headers=auth_headers)
    data = response.json()
    return (
        data.get("data", {}).get("id")
        or data.get("data", {}).get("_id")
        or data.get("id")
        or data.get("_id")
    )


# ──────────────────────────────────────────────
# POSITIVE TESTS
# ──────────────────────────────────────────────

class TestGetCurrentUser:
    def test_get_me_returns_200(self, base_url, auth_headers):
        """GET /users/me with valid token should return 200."""
        response = requests.get(f"{base_url}/users/me", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    def test_get_me_response_has_email_field(self, base_url, auth_headers):
        """GET /users/me response must contain an email field."""
        response = requests.get(f"{base_url}/users/me", headers=auth_headers)
        data = response.json()
        user = data.get("data") or data
        assert "email" in user, f"No 'email' in /users/me response: {data}"

    def test_get_me_email_is_string(self, base_url, auth_headers):
        """Email field in /users/me response must be a string."""
        response = requests.get(f"{base_url}/users/me", headers=auth_headers)
        data = response.json()
        user = data.get("data") or data
        assert isinstance(user.get("email"), str)

    def test_get_me_response_has_id_field(self, base_url, auth_headers):
        """GET /users/me response must contain a user ID field."""
        response = requests.get(f"{base_url}/users/me", headers=auth_headers)
        data = response.json()
        user = data.get("data") or data
        has_id = "id" in user or "_id" in user
        assert has_id, f"No id/_id in /users/me response: {data}"


class TestGetUserById:
    def test_get_user_by_valid_id_returns_200(self, base_url, auth_headers):
        """GET /users/{userId} with the current user's own ID should return 200."""
        user_id = get_current_user_id(base_url, auth_headers)
        assert user_id, "Could not retrieve current user ID"
        response = requests.get(f"{base_url}/users/{user_id}", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    def test_get_user_by_valid_id_response_has_email(self, base_url, auth_headers):
        """GET /users/{userId} response must include the user's email."""
        user_id = get_current_user_id(base_url, auth_headers)
        response = requests.get(f"{base_url}/users/{user_id}", headers=auth_headers)
        data = response.json()
        user = data.get("data") or data
        assert "email" in user, f"No email in user-by-id response: {data}"


class TestGetUserOrganisations:
    def test_get_user_organisations_returns_200(self, base_url, auth_headers):
        """GET /users/organisations should return 200 for authenticated user."""
        response = requests.get(f"{base_url}/users/organisations", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    def test_get_user_organisations_returns_list(self, base_url, auth_headers):
        """GET /users/organisations response should contain a list."""
        response = requests.get(f"{base_url}/users/organisations", headers=auth_headers)
        data = response.json()
        orgs = data.get("data") or data
        assert isinstance(orgs, list), f"Expected list for organisations, got: {type(orgs)}"


class TestNotificationPreferences:
    def test_get_notification_preferences_returns_200(self, base_url, auth_headers):
        """GET /users/notification-preferences should return 200."""
        response = requests.get(f"{base_url}/users/notification-preferences", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    def test_update_notification_preferences_returns_success(self, base_url, auth_headers):
        """PUT /users/notification-preferences with valid payload should return 200."""
        payload = {"email_notifications": True, "push_notifications": False}
        response = requests.put(
            f"{base_url}/users/notification-preferences",
            headers=auth_headers,
            json=payload,
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"


# ──────────────────────────────────────────────
# NEGATIVE TESTS
# ──────────────────────────────────────────────

class TestUsersNegative:
    def test_get_me_without_token_returns_401(self, base_url):
        """GET /users/me without Authorization header should return 401."""
        response = requests.get(f"{base_url}/users/me")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"

    def test_get_me_with_invalid_token_returns_401(self, base_url):
        """GET /users/me with a fake token should return 401."""
        headers = {"Authorization": "Bearer this.is.a.fake.token"}
        response = requests.get(f"{base_url}/users/me", headers=headers)
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"

    def test_get_me_with_malformed_auth_header_returns_401(self, base_url):
        """GET /users/me with malformed Authorization (no 'Bearer') should return 401."""
        headers = {"Authorization": "NotBearer sometoken"}
        response = requests.get(f"{base_url}/users/me", headers=headers)
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"

    def test_get_user_by_nonexistent_id_returns_404(self, base_url, auth_headers):
        """GET /users/{userId} with a random non-existent ID should return 404."""
        fake_id = str(uuid.uuid4())
        response = requests.get(f"{base_url}/users/{fake_id}", headers=auth_headers)
        assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"

    def test_get_organisations_without_token_returns_401(self, base_url):
        """GET /users/organisations without token should return 401."""
        response = requests.get(f"{base_url}/users/organisations")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"


# ──────────────────────────────────────────────
# EDGE CASE TESTS
# ──────────────────────────────────────────────

class TestUsersEdgeCases:
    def test_get_user_by_empty_string_id_returns_error(self, base_url, auth_headers):
        """GET /users/ with an empty ID segment should return 404 or 405."""
        response = requests.get(f"{base_url}/users/", headers=auth_headers)
        assert response.status_code in (404, 405), (
            f"Expected 404 or 405, got {response.status_code}"
        )

    def test_get_user_by_special_characters_id_does_not_crash(self, base_url, auth_headers):
        """GET /users/{id} with special characters should return a clean error, not 500."""
        response = requests.get(f"{base_url}/users/!@#$%^&*()", headers=auth_headers)
        assert response.status_code != 500, "Server returned 500 on special character user ID"

    def test_get_user_by_very_long_id_does_not_crash(self, base_url, auth_headers):
        """GET /users/{id} with an extremely long ID should not return 500."""
        long_id = "a" * 500
        response = requests.get(f"{base_url}/users/{long_id}", headers=auth_headers)
        assert response.status_code != 500, "Server returned 500 on very long user ID"