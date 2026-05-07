import uuid
import requests
import pytest

ORG_ID = "019de302-9c35-7a83-9c72-177d901cd4c1"


def create_test_channel(base_url, auth_headers):
    """Helper to create a test channel. Channels require org_id in the request body."""
    payload = {
        "name": f"test-channel-{uuid.uuid4().hex[:8]}",
        "description": "Automated test channel",
        "org_id": ORG_ID,
    }
    return requests.post(f"{base_url}/channels", headers=auth_headers, json=payload)


def get_channels_url(base_url):
    """Channels list endpoint requires org_id in the URL path."""
    return f"{base_url}/organisations/{ORG_ID}/channels"


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
        """GET /organisations/{org_id}/channels should return 200."""
        response = requests.get(get_channels_url(base_url), headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    def test_get_channels_returns_list(self, base_url, auth_headers):
        """GET channels should return a list (array) of channels."""
        response = requests.get(get_channels_url(base_url), headers=auth_headers)
        data = response.json()
        channels = data.get("data") or data
        assert isinstance(channels, list), f"Expected list, got: {type(channels)}: {data}"

    def test_get_channels_response_is_json(self, base_url, auth_headers):
        """GET channels should return a JSON response."""
        response = requests.get(get_channels_url(base_url), headers=auth_headers)
        assert "application/json" in response.headers.get("Content-Type", "")


class TestGetChannelById:
    @pytest.fixture
    def channel_id(self, base_url, auth_headers):
        """Get an existing channel ID from the org."""
        response = requests.get(get_channels_url(base_url), headers=auth_headers)
        if response.status_code != 200:
            return None
        data = response.json()
        channels = data.get("data") or []
        if not channels:
            return None
        return channels[0].get("id") or channels[0].get("_id")

    def test_get_channel_by_valid_id_returns_200(self, base_url, auth_headers, channel_id):
        """GET /channels/{id} with a valid ID should return 200."""
        if not channel_id:
            pytest.skip("No channels available to test")
        response = requests.get(f"{base_url}/channels/{channel_id}/", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    def test_get_channel_by_id_response_has_name(self, base_url, auth_headers, channel_id):
        """GET /channels/{id} response should include a name field."""
        if not channel_id:
            pytest.skip("No channels available to test")
        response = requests.get(f"{base_url}/channels/{channel_id}/", headers=auth_headers)
        data = response.json()
        channel = data.get("data") or data
        assert "name" in channel, f"No 'name' in channel response: {data}"


class TestChannelUsers:
    @pytest.fixture
    def channel_id(self, base_url, auth_headers):
        response = requests.get(get_channels_url(base_url), headers=auth_headers)
        if response.status_code != 200:
            return None
        data = response.json()
        channels = data.get("data") or []
        if not channels:
            return None
        return channels[0].get("id") or channels[0].get("_id")

    def test_get_channel_users_returns_200(self, base_url, auth_headers, channel_id):
        """GET /channels/{id}/users should return 200."""
        if not channel_id:
            pytest.skip("No channels available to test")
        response = requests.get(f"{base_url}/channels/{channel_id}/users", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    def test_get_channel_num_users_returns_200(self, base_url, auth_headers, channel_id):
        """GET /channels/{id}/num-users should return 200."""
        if not channel_id:
            pytest.skip("No channels available to test")
        response = requests.get(f"{base_url}/channels/{channel_id}/num-users", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"


class TestChannelsNegative:
    def test_get_channels_without_token_returns_401(self, base_url):
        """GET channels without token should return 401."""
        response = requests.get(get_channels_url(base_url))
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"

    def test_create_channel_without_token_returns_401(self, base_url):
        """POST /channels without token should return 401."""
        payload = {"name": "no-auth-channel", "org_id": ORG_ID}
        response = requests.post(f"{base_url}/channels", json=payload)
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"

    def test_get_channel_by_nonexistent_id_returns_error(self, base_url, auth_headers):
        """GET /channels/{id} with a fake ID should return 400 or 404."""
        fake_id = str(uuid.uuid4())
        response = requests.get(f"{base_url}/channels/{fake_id}/", headers=auth_headers)
        # Zedu returns 400 ("record not found") not 404
        assert response.status_code in (400, 404), (
            f"Expected 400 or 404, got {response.status_code}: {response.text}"
        )

    def test_create_channel_without_name_returns_400(self, base_url, auth_headers):
        """POST /channels without a name should return 400."""
        payload = {"description": "No name channel", "org_id": ORG_ID}
        response = requests.post(f"{base_url}/channels", headers=auth_headers, json=payload)
        assert response.status_code in (400, 422), f"Expected 400 or 422, got {response.status_code}"

    def test_get_channels_with_invalid_token_returns_401(self, base_url):
        """GET channels with a fake token should return 401."""
        headers = {"Authorization": "Bearer fake.token.here"}
        response = requests.get(get_channels_url(base_url), headers=headers)
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"

    def test_get_channel_users_without_token_returns_401(self, base_url):
        """GET /channels/{id}/users without token should return 401 or 404."""
        fake_id = str(uuid.uuid4())
        response = requests.get(f"{base_url}/channels/{fake_id}/users")
        assert response.status_code in (401, 404), f"Expected 401 or 404, got {response.status_code}"


class TestChannelsEdgeCases:
    def test_create_channel_with_very_long_name_does_not_crash(self, base_url, auth_headers):
        """POST /channels with a very long name should not crash the server."""
        payload = {"name": "x" * 300, "org_id": ORG_ID}
        response = requests.post(f"{base_url}/channels", headers=auth_headers, json=payload)
        assert response.status_code < 500, "Server crashed on very long channel name"

    def test_create_channel_with_special_chars_in_name(self, base_url, auth_headers):
        """POST /channels with special characters in name should not crash."""
        payload = {"name": "test !@#$% channel", "org_id": ORG_ID}
        response = requests.post(f"{base_url}/channels", headers=auth_headers, json=payload)
        assert response.status_code < 500, f"Unexpected status for special char name: {response.status_code}"

    def test_get_channel_by_numeric_id_does_not_crash(self, base_url, auth_headers):
        """GET /channels/{id} with a numeric ID should not crash the server."""
        response = requests.get(f"{base_url}/channels/12345/", headers=auth_headers)
        assert response.status_code < 500, "Server crashed on numeric channel ID"