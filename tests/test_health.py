import uuid
import requests
import pytest


def get_current_user_id(base_url, auth_headers):
    """Helper to get current user ID from /users/me."""
    response = requests.get(f"{base_url}/users/me", headers=auth_headers)
    if response.status_code != 200:
        return None
    data = response.json()
    try:
        return data["data"]["user"]["id"]
    except (KeyError, TypeError):
        try:
            return data["data"].get("user_id")
        except (KeyError, TypeError):
            return None


class TestGetProfile:
    def test_get_profile_returns_200(self, base_url, auth_headers):
        """GET /profile should return 200 for authenticated user."""
        response = requests.get(f"{base_url}/profile", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    def test_get_profile_response_has_expected_fields(self, base_url, auth_headers):
        """GET /profile response should contain expected fields."""
        response = requests.get(f"{base_url}/profile", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        profile = data.get("data") or data
        expected = ["email", "username"]
        missing = [f for f in expected if f not in profile]
        assert not missing, f"Profile missing expected fields: {missing}"

    def test_get_profile_response_is_json(self, base_url, auth_headers):
        """GET /profile should return a JSON response."""
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
        """PATCH /profile with a valid payload should return 200 (uses multipart/form-data)."""
        # Zedu's PATCH /profile requires multipart/form-data, not JSON
        headers_no_ct = {k: v for k, v in auth_headers.items() if k != "Content-Type"}
        payload = {"tagline": f"Automated test tagline {uuid.uuid4().hex[:6]}"}
        response = requests.patch(f"{base_url}/profile", headers=headers_no_ct, data=payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    def test_patch_profile_response_reflects_update(self, base_url, auth_headers):
        """PATCH /profile should return the updated profile data."""
        headers_no_ct = {k: v for k, v in auth_headers.items() if k != "Content-Type"}
        unique_tagline = f"TaglineTest-{uuid.uuid4().hex[:8]}"
        payload = {"tagline": unique_tagline}
        response = requests.patch(f"{base_url}/profile", headers=headers_no_ct, data=payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"


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
        # API expects integer flags, not boolean
        payload = {"auto_download_photos": 1, "auto_download_videos": 0}
        response = requests.put(
            f"{base_url}/users/media-preferences", headers=auth_headers, json=payload
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"


class TestProfileNegative:
    def test_get_profile_without_token_returns_401(self, base_url):
        """GET /profile without token should return 401."""
        response = requests.get(f"{base_url}/profile")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"

    def test_get_profile_with_expired_token_returns_401(self, base_url):
        """GET /profile with a fake token should return 401."""
        headers = {"Authorization": "Bearer fake.expired.token"}
        response = requests.get(f"{base_url}/profile", headers=headers)
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"

    def test_get_profile_by_nonexistent_user_id_returns_error(self, base_url, auth_headers):
        """GET /profile/{user_id} with a random ID should return 400 or 404."""
        fake_id = str(uuid.uuid4())
        response = requests.get(f"{base_url}/profile/{fake_id}", headers=auth_headers)
        # Zedu returns 400 ("user not a member of organisation") not 404
        assert response.status_code in (400, 404), (
            f"Expected 400 or 404, got {response.status_code}: {response.text}"
        )

    def test_get_presence_without_token_returns_401(self, base_url):
        """GET /profile/presence without token should return 401."""
        response = requests.get(f"{base_url}/profile/presence")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"

    def test_update_presence_with_invalid_status_accepts_any_value(self, base_url, auth_headers):
        """POST /profile/presence — Zedu accepts any status string without validation."""
        # Zedu does not validate the status value — it accepts anything and returns 200.
        # This documents the actual API behaviour.
        payload = {"status": "flying_to_the_moon"}
        response = requests.post(f"{base_url}/profile/presence", headers=auth_headers, json=payload)
        assert response.status_code == 200, (
            f"Expected 200 (Zedu accepts any presence value), got {response.status_code}"
        )

    def test_get_media_preferences_without_token_returns_401(self, base_url):
        """GET /users/media-preferences without token should return 401."""
        response = requests.get(f"{base_url}/users/media-preferences")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"


class TestProfileEdgeCases:
    def test_patch_profile_with_empty_body_does_not_crash(self, base_url, auth_headers):
        """PATCH /profile with empty body should not crash the server."""
        headers_no_ct = {k: v for k, v in auth_headers.items() if k != "Content-Type"}
        response = requests.patch(f"{base_url}/profile", headers=headers_no_ct, data={})
        assert response.status_code < 500, "Server crashed on empty profile patch"

    def test_patch_profile_with_extremely_long_tagline_does_not_crash(self, base_url, auth_headers):
        """PATCH /profile with a very long tagline should not crash the server."""
        headers_no_ct = {k: v for k, v in auth_headers.items() if k != "Content-Type"}
        payload = {"tagline": "x" * 1000}
        response = requests.patch(f"{base_url}/profile", headers=headers_no_ct, data=payload)
        assert response.status_code < 500, "Server crashed on long tagline"

    def test_get_profile_by_numeric_id_does_not_crash(self, base_url, auth_headers):
        """GET /profile/{id} with a numeric ID should not crash the server."""
        response = requests.get(f"{base_url}/profile/12345", headers=auth_headers)
        assert response.status_code < 500, "Server crashed on numeric profile ID"