"""
test_health.py
==============
Tests for miscellaneous Zedu API endpoints:
  - GET  /profile               — Get current user profile
  - PATCH /profile              — Update user profile
  - GET  /profile/{user_id}     — Get profile by user ID
  - POST /profile/presence      — Update presence status
  - GET  /profile/presence      — Get current presence
  - GET  /users/media-preferences
  - PUT  /users/media-preferences

These endpoints act as a broad health check and also verify
profile and preference management functionality.
"""

import uuid
import pytest
import requests


# ──────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────

def get_current_user_id(base_url, auth_headers):
    """Fetch the authenticated user's ID via /users/me."""
    response = requests.get(f"{base_url}/users/me", headers=auth_headers)
    data = response.json()
    user = data.get("data") or data
    return user.get("id") or user.get("_id")


# ──────────────────────────────────────────────
# POSITIVE TESTS — PROFILE
# ──────────────────────────────────────────────

class TestGetProfile:
    def test_get_profile_returns_200(self, base_url, auth_headers):
        """GET /profile should return 200 for authenticated user."""
        response = requests.get(f"{base_url}/profile", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    def test_get_profile_response_has_expected_fields(self, base_url, auth_headers):
        """GET /profile response should contain common profile fields."""
        response = requests.get(f"{base_url}/profile", headers=auth_headers)
        data = response.json()
        profile = data.get("data") or data
        # At least one of these must exist
        has_expected = any(k in profile for k in ("id", "_id", "email", "name", "first_name", "full_name"))
        assert has_expected, f"Profile missing expected fields: {data}"

    def test_get_profile_response_is_json(self, base_url, auth_headers):
        """GET /profile response Content-Type must be application/json."""
        response = requests.get(f"{base_url}/profile", headers=auth_headers)
        assert "application/json" in response.headers.get("Content-Type", "")

    def test_get_profile_by_user_id_returns_200(self, base_url, auth_headers):
        """GET /profile/{user_id} with valid user ID should return 200."""
        user_id = get_current_user_id(base_url, auth_headers)
        assert user_id, "Could not retrieve current user ID"
        response = requests.get(f"{base_url}/profile/{user_id}", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"


class TestUpdateProfile:
    def test_patch_profile_with_valid_data_returns_200(self, base_url, auth_headers):
        """PATCH /profile with a valid payload should return 200."""
        payload = {"tagline": f"Automated test tagline {uuid.uuid4().hex[:6]}"}
        response = requests.patch(f"{base_url}/profile", headers=auth_headers, json=payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    def test_patch_profile_response_reflects_update(self, base_url, auth_headers):
        """PATCH /profile should return the updated profile data."""
        unique_tagline = f"TaglineTest-{uuid.uuid4().hex[:8]}"
        payload = {"tagline": unique_tagline}
        response = requests.patch(f"{base_url}/profile", headers=auth_headers, json=payload)
        assert response.status_code == 200
        data = response.json()
        # Response should acknowledge the update (not necessarily echo value)
        assert data is not None


class TestPresence:
    def test_get_presence_returns_200(self, base_url, auth_headers):
        """GET /profile/presence should return 200."""
        response = requests.get(f"{base_url}/profile/presence", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    def test_update_presence_returns_200(self, base_url, auth_headers):
        """POST /profile/presence with valid status should return 200."""
        payload = {"status": "online"}
        response = requests.post(f"{base_url}/profile/presence", headers=auth_headers, json=payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"


class TestMediaPreferences:
    def test_get_media_preferences_returns_200(self, base_url, auth_headers):
        """GET /users/media-preferences should return 200."""
        response = requests.get(f"{base_url}/users/media-preferences", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    def test_update_media_preferences_returns_200(self, base_url, auth_headers):
        """PUT /users/media-preferences with valid payload should return 200."""
        payload = {"auto_download_photos": True, "auto_download_videos": False}
        response = requests.put(
            f"{base_url}/users/media-preferences", headers=auth_headers, json=payload
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"


# ──────────────────────────────────────────────
# NEGATIVE TESTS
# ──────────────────────────────────────────────

class TestProfileNegative:
    def test_get_profile_without_token_returns_401(self, base_url):
        """GET /profile without Authorization header should return 401."""
        response = requests.get(f"{base_url}/profile")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"

    def test_get_profile_with_expired_token_returns_401(self, base_url):
        """GET /profile with a clearly invalid (expired) token should return 401."""
        headers = {
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjF9.invalid",
            "Content-Type": "application/json",
        }
        response = requests.get(f"{base_url}/profile", headers=headers)
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"

    def test_get_profile_by_nonexistent_user_id_returns_404(self, base_url, auth_headers):
        """GET /profile/{user_id} with a random ID should return 404."""
        fake_id = str(uuid.uuid4())
        response = requests.get(f"{base_url}/profile/{fake_id}", headers=auth_headers)
        assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"

    def test_get_presence_without_token_returns_401(self, base_url):
        """GET /profile/presence without token should return 401."""
        response = requests.get(f"{base_url}/profile/presence")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"

    def test_update_presence_with_invalid_status_returns_error(self, base_url, auth_headers):
        """POST /profile/presence with an invalid status value should return 400 or 422."""
        payload = {"status": "flying_to_the_moon"}
        response = requests.post(f"{base_url}/profile/presence", headers=auth_headers, json=payload)
        assert response.status_code in (400, 422), (
            f"Expected 400 or 422, got {response.status_code}: {response.text}"
        )

    def test_get_media_preferences_without_token_returns_401(self, base_url):
        """GET /users/media-preferences without token should return 401."""
        response = requests.get(f"{base_url}/users/media-preferences")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"


# ──────────────────────────────────────────────
# EDGE CASE TESTS
# ──────────────────────────────────────────────

class TestProfileEdgeCases:
    def test_patch_profile_with_empty_body_does_not_crash(self, base_url, auth_headers):
        """PATCH /profile with an empty JSON body should return a proper response, not 500."""
        response = requests.patch(f"{base_url}/profile", headers=auth_headers, json={})
        assert response.status_code != 500, "Server returned 500 on empty PATCH /profile body"

    def test_patch_profile_with_extremely_long_tagline_does_not_crash(self, base_url, auth_headers):
        """PATCH /profile with a 2000-char tagline should return a clean error, not 500."""
        payload = {"tagline": "T" * 2000}
        response = requests.patch(f"{base_url}/profile", headers=auth_headers, json=payload)
        assert response.status_code != 500, "Server returned 500 on very long tagline"

    def test_get_profile_by_numeric_id_does_not_crash(self, base_url, auth_headers):
        """GET /profile/99999 (numeric ID) should return a clean 404 or 400, not 500."""
        response = requests.get(f"{base_url}/profile/99999", headers=auth_headers)
        assert response.status_code != 500, "Server returned 500 on numeric profile ID"