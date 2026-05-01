"""
test_channels.py
================
Tests for the Zedu channel endpoints:
  - POST /channels          — Create channel
  - GET  /channels          — List channels
  - GET  /channels/{id}/    — Get channel by ID
  - GET  /channels/{id}/users
  - GET  /channels/{id}/num-users

Note: Org-specific channel endpoints are skipped as org ID
is not required for this test suite.
"""

import uuid
import pytest
import requests


def create_test_channel(base_url, auth_headers, name=None):
    channel_name = name or f"test-channel-{uuid.uuid4().hex[:8]}"
    payload = {
        "name": channel_name,
        "description": "Automated test channel",
        "is_private": False,
    }
    return requests.post(f"{base_url}/channels", headers=auth_headers, json=payload)


def get_channel_id_from_list(base_url, auth_headers):
    """Get the first available channel ID from the channels list."""
    response = requests.get(f"{base_url}/channels", headers=auth_headers)
    data = response.json()
    channels = data.get("data") or data
    if isinstance(channels, list) and len(channels) > 0:
        ch = channels[0]
        return ch.get("id") or ch.get("_id")
    return None


# ──────────────────────────────────────────────
# POSITIVE TESTS
# ──────────────────────────────────────────────

class TestCreateChannel:
    def test_create_channel_returns_200_or_201(self, base_url, auth_headers):
        """POST /channels with valid payload should return 200 or 201."""
        response = create_test_channel(base_url, auth_headers)
        assert response.status_code in (200, 201), (
            f"Expected 200 or 201, got {response.status_code}: {response.text}"
        )

    def test_create_channel_response_has_id_field(self, base_url, auth_headers):
        """Created channel response must include an ID field."""
        response = create_test_channel(base_url, auth_headers)
        data = response.json()
        channel = data.get("data") or data
        has_id = "id" in channel or "_id" in channel
        assert has_id, f"No id/_id in create channel response: {data}"

    def test_create_channel_response_has_name_field(self, base_url, auth_headers):
        """Created channel response must include the channel name."""
        response = create_test_channel(base_url, auth_headers)
        data = response.json()
        channel = data.get("data") or data
        assert "name" in channel, f"No 'name' in create channel response: {data}"


class TestListChannels:
    def test_get_channels_returns_200(self, base_url, auth_headers):
        """GET /channels should return 200 for an authenticated user."""
        response = requests.get(f"{base_url}/channels", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    def test_get_channels_returns_list(self, base_url, auth_headers):
        """GET /channels should return a list (array) of channels."""
        response = requests.get(f"{base_url}/channels", headers=auth_headers)
        data = response.json()
        channels = data.get("data") or data
        assert isinstance(channels, list), f"Expected list, got: {type(channels)}: {data}"

    def test_get_channels_response_is_json(self, base_url, auth_headers):
        """GET /channels response Content-Type must be application/json."""
        response = requests.get(f"{base_url}/channels", headers=auth_headers)
        assert "application/json" in response.headers.get("Content-Type", "")


class TestGetChannelById:
    def test_get_channel_by_valid_id_returns_200(self, base_url, auth_headers):
        """GET /channels/{id}/ with a real channel ID should return 200."""
        channel_id = get_channel_id_from_list(base_url, auth_headers)
        if not channel_id:
            pytest.skip("No channels available to test with")
        response = requests.get(f"{base_url}/channels/{channel_id}/", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    def test_get_channel_by_id_response_has_name(self, base_url, auth_headers):
        """GET /channels/{id}/ response must include the channel name."""
        channel_id = get_channel_id_from_list(base_url, auth_headers)
        if not channel_id:
            pytest.skip("No channels available to test with")
        response = requests.get(f"{base_url}/channels/{channel_id}/", headers=auth_headers)
        data = response.json()
        channel = data.get("data") or data
        assert "name" in channel, f"No 'name' in channel response: {data}"


class TestChannelUsers:
    def test_get_channel_users_returns_200(self, base_url, auth_headers):
        """GET /channels/{id}/users should return 200."""
        channel_id = get_channel_id_from_list(base_url, auth_headers)
        if not channel_id:
            pytest.skip("No channels available to test with")
        response = requests.get(f"{base_url}/channels/{channel_id}/users", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    def test_get_channel_num_users_returns_200(self, base_url, auth_headers):
        """GET /channels/{id}/num-users should return 200."""
        channel_id = get_channel_id_from_list(base_url, auth_headers)
        if not channel_id:
            pytest.skip("No channels available to test with")
        response = requests.get(f"{base_url}/channels/{channel_id}/num-users", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"


# ──────────────────────────────────────────────
# NEGATIVE TESTS
# ──────────────────────────────────────────────

class TestChannelsNegative:
    def test_get_channels_without_token_returns_401(self, base_url):
        """GET /channels without token should return 401."""
        response = requests.get(f"{base_url}/channels")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"

    def test_create_channel_without_token_returns_401(self, base_url):
        """POST /channels without token should return 401."""
        payload = {"name": "unauth-channel"}
        response = requests.post(f"{base_url}/channels", json=payload)
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"

    def test_get_channel_by_nonexistent_id_returns_404(self, base_url, auth_headers):
        """GET /channels/{id}/ with a fake ID should return 404."""
        fake_id = str(uuid.uuid4())
        response = requests.get(f"{base_url}/channels/{fake_id}/", headers=auth_headers)
        assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"

    def test_create_channel_without_name_returns_400(self, base_url, auth_headers):
        """POST /channels without a name field should return 400."""
        payload = {"description": "No name channel"}
        response = requests.post(f"{base_url}/channels", headers=auth_headers, json=payload)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"

    def test_get_channels_with_invalid_token_returns_401(self, base_url):
        """GET /channels with a fake token should return 401."""
        headers = {"Authorization": "Bearer fake.token.here"}
        response = requests.get(f"{base_url}/channels", headers=headers)
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"

    def test_get_channel_users_without_token_returns_401(self, base_url, auth_headers):
        """GET /channels/{id}/users without token should return 401."""
        channel_id = get_channel_id_from_list(base_url, auth_headers)
        if not channel_id:
            pytest.skip("No channels available to test with")
        response = requests.get(f"{base_url}/channels/{channel_id}/users")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"


# ──────────────────────────────────────────────
# EDGE CASE TESTS
# ──────────────────────────────────────────────

class TestChannelsEdgeCases:
    def test_create_channel_with_very_long_name_does_not_crash(self, base_url, auth_headers):
        """POST /channels with a 500-char name should return a proper error, not 500."""
        payload = {"name": "x" * 500, "description": "Edge case long name"}
        response = requests.post(f"{base_url}/channels", headers=auth_headers, json=payload)
        assert response.status_code != 500, "Server crashed on long channel name"

    def test_create_channel_with_special_chars_in_name(self, base_url, auth_headers):
        """POST /channels with special chars in name should return a clean response."""
        payload = {"name": "!@#channel$$%^", "description": "Special chars test"}
        response = requests.post(f"{base_url}/channels", headers=auth_headers, json=payload)
        assert response.status_code in (200, 201, 400, 422), (
            f"Unexpected status for special char name: {response.status_code}"
        )

    def test_get_channel_by_numeric_id_does_not_crash(self, base_url, auth_headers):
        """GET /channels/12345/ with a numeric string ID should not 500."""
        response = requests.get(f"{base_url}/channels/12345/", headers=auth_headers)
        assert response.status_code != 500, "Server returned 500 on numeric channel ID"