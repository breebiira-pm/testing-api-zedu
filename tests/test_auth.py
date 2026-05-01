"""
test_auth.py
============
Tests for the Zedu authentication endpoints:
  - POST /auth/register
  - POST /auth/login
  - POST /auth/logout
  - POST /auth/password-reset
"""

import uuid
import pytest
import requests


# ──────────────────────────────────────────────
# POSITIVE TESTS
# ──────────────────────────────────────────────

class TestLogin:
    def test_login_with_valid_credentials_returns_200(self, base_url, registered_user_credentials):
        """Login with correct email and password should return 200 and a token."""
        response = requests.post(f"{base_url}/auth/login", json=registered_user_credentials)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    def test_login_response_contains_access_token(self, base_url, registered_user_credentials):
        """Login response must include an access token field."""
        response = requests.post(f"{base_url}/auth/login", json=registered_user_credentials)
        data = response.json()
        token = (
            data.get("access_token")
            or data.get("token")
            or data.get("data", {}).get("access_token")
            or data.get("data", {}).get("token")
        )
        assert token is not None, f"No token found in login response: {data}"
        assert isinstance(token, str)
        assert len(token) > 10

    def test_login_response_content_type_is_json(self, base_url, registered_user_credentials):
        """Login response Content-Type should be application/json."""
        response = requests.post(f"{base_url}/auth/login", json=registered_user_credentials)
        assert "application/json" in response.headers.get("Content-Type", "")

    def test_login_response_time_is_acceptable(self, base_url, registered_user_credentials):
        """Login response should complete within 10 seconds."""
        response = requests.post(f"{base_url}/auth/login", json=registered_user_credentials)
        assert response.elapsed.total_seconds() < 10


class TestRegister:
    def test_register_new_user_returns_success(self, base_url, unique_email):
        """Registering a brand-new unique email should succeed."""
        payload = {
            "email": unique_email,
            "password": "SecurePass@123",
            "full_name": "Test Automation User",
        }
        response = requests.post(f"{base_url}/auth/register", json=payload)
        assert response.status_code in (200, 201), (
            f"Expected 200 or 201, got {response.status_code}: {response.text}"
        )

    def test_register_response_has_user_field(self, base_url, unique_email):
        """Register response should include user data or a confirmation message."""
        payload = {
            "email": unique_email,
            "password": "SecurePass@123",
            "full_name": "Test Automation User",
        }
        response = requests.post(f"{base_url}/auth/register", json=payload)
        data = response.json()
        assert (
            "user" in data
            or "data" in data
            or "message" in data
            or "email" in str(data).lower()
        ), f"Unexpected register response shape: {data}"


class TestLogout:
    def test_logout_with_valid_token_returns_success(self, base_url, auth_headers):
        """Logout with a valid token should return 200."""
        response = requests.post(f"{base_url}/auth/logout", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"


# ──────────────────────────────────────────────
# NEGATIVE TESTS
# ──────────────────────────────────────────────

class TestLoginNegative:
    def test_login_with_wrong_password_returns_error(self, base_url, registered_user_credentials):
        """Login with a wrong password must return an error (400 or 401)."""
        payload = {
            "email": registered_user_credentials["email"],
            "password": "WrongPassword999!",
        }
        response = requests.post(f"{base_url}/auth/login", json=payload)
        # Zedu returns 400 for invalid credentials
        assert response.status_code in (400, 401), (
            f"Expected 400 or 401, got {response.status_code}: {response.text}"
        )

    def test_login_with_wrong_password_returns_error_message(self, base_url, registered_user_credentials):
        """Login with wrong password response must contain an error message."""
        payload = {
            "email": registered_user_credentials["email"],
            "password": "WrongPassword999!",
        }
        response = requests.post(f"{base_url}/auth/login", json=payload)
        data = response.json()
        assert "message" in data or "error" in data, f"No error message in response: {data}"

    def test_login_with_nonexistent_email_returns_error(self, base_url):
        """Login with an email that does not exist should return an error."""
        payload = {
            "email": f"ghost_{uuid.uuid4().hex}@nowhere.com",
            "password": "AnyPassword123!",
        }
        response = requests.post(f"{base_url}/auth/login", json=payload)
        # Zedu returns 400 for invalid credentials
        assert response.status_code in (400, 401, 404), (
            f"Expected 400, 401 or 404, got {response.status_code}: {response.text}"
        )

    def test_login_with_missing_password_returns_400(self, base_url, registered_user_credentials):
        """Login without a password field should return 400 Bad Request."""
        payload = {"email": registered_user_credentials["email"]}
        response = requests.post(f"{base_url}/auth/login", json=payload)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"

    def test_login_with_missing_email_returns_400(self, base_url):
        """Login without an email field should return 400 Bad Request."""
        payload = {"password": "SomePassword123!"}
        response = requests.post(f"{base_url}/auth/login", json=payload)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"

    def test_login_with_empty_body_returns_400(self, base_url):
        """Login with an empty JSON body should return 400 Bad Request."""
        response = requests.post(f"{base_url}/auth/login", json={})
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"

    def test_login_error_response_has_message_field(self, base_url):
        """A failed login response should contain an error or message field."""
        payload = {"email": "bad@bad.com", "password": "badpass"}
        response = requests.post(f"{base_url}/auth/login", json=payload)
        data = response.json()
        assert (
            "message" in data or "error" in data or "detail" in data
        ), f"No error message in failed login response: {data}"


class TestRegisterNegative:
    def test_register_duplicate_email_returns_error(self, base_url, registered_user_credentials):
        """Registering with an already-existing email should return 400 or 409."""
        payload = {
            "email": registered_user_credentials["email"],
            "password": "SecurePass@123",
            "full_name": "Duplicate User",
        }
        response = requests.post(f"{base_url}/auth/register", json=payload)
        # Zedu returns 400 for duplicate email
        assert response.status_code in (400, 409), (
            f"Expected 400 or 409, got {response.status_code}: {response.text}"
        )

    def test_register_duplicate_email_returns_helpful_message(self, base_url, registered_user_credentials):
        """Duplicate email registration response should contain a helpful message."""
        payload = {
            "email": registered_user_credentials["email"],
            "password": "SecurePass@123",
            "full_name": "Duplicate User",
        }
        response = requests.post(f"{base_url}/auth/register", json=payload)
        data = response.json()
        assert "message" in data, f"No message in duplicate register response: {data}"

    def test_register_with_invalid_email_format_returns_400(self, base_url):
        """Registering with a malformed email should return 400 or 422."""
        payload = {
            "email": "not-an-email",
            "password": "SecurePass@123",
            "full_name": "Bad Email User",
        }
        response = requests.post(f"{base_url}/auth/register", json=payload)
        assert response.status_code in (400, 422), (
            f"Expected 400 or 422, got {response.status_code}: {response.text}"
        )

    def test_register_without_email_returns_error(self, base_url):
        """Registering without an email field should return 400 or 422."""
        payload = {"password": "SecurePass@123", "full_name": "No Email User"}
        response = requests.post(f"{base_url}/auth/register", json=payload)
        assert response.status_code in (400, 422), (
            f"Expected 400 or 422, got {response.status_code}: {response.text}"
        )

    def test_register_without_password_returns_error(self, base_url, unique_email):
        """Registering without a password field should return 400 or 422."""
        payload = {"email": unique_email, "full_name": "No Password User"}
        response = requests.post(f"{base_url}/auth/register", json=payload)
        assert response.status_code in (400, 422), (
            f"Expected 400 or 422, got {response.status_code}: {response.text}"
        )


# ──────────────────────────────────────────────
# EDGE CASE TESTS
# ──────────────────────────────────────────────

class TestAuthEdgeCases:
    def test_login_email_with_leading_trailing_spaces(self, base_url, registered_user_credentials):
        """Email with leading/trailing whitespace should fail or be trimmed."""
        payload = {
            "email": f"  {registered_user_credentials['email']}  ",
            "password": registered_user_credentials["password"],
        }
        response = requests.post(f"{base_url}/auth/login", json=payload)
        assert response.status_code in (200, 400, 401), (
            f"Unexpected status for padded email: {response.status_code}"
        )

    def test_login_with_very_long_password_does_not_crash(self, base_url, registered_user_credentials):
        """A very long password string should return a proper error, not a 500."""
        payload = {
            "email": registered_user_credentials["email"],
            "password": "A" * 1000,
        }
        response = requests.post(f"{base_url}/auth/login", json=payload)
        assert response.status_code != 500, "Server crashed with 500 on long password"

    def test_login_with_sql_injection_in_email_does_not_crash(self, base_url):
        """SQL injection in email field should be rejected gracefully, not crash."""
        payload = {
            "email": "' OR '1'='1",
            "password": "anything",
        }
        response = requests.post(f"{base_url}/auth/login", json=payload)
        assert response.status_code in (400, 401, 422), (
            f"SQL injection attempt got unexpected response: {response.status_code}"
        )

    def test_password_reset_request_with_valid_email(self, base_url, registered_user_credentials):
        """Password reset request with a registered email should return 200."""
        payload = {"email": registered_user_credentials["email"]}
        response = requests.post(f"{base_url}/auth/password-reset", json=payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    def test_password_reset_request_with_unknown_email(self, base_url):
        """Password reset for unknown email should return 200 or 404."""
        payload = {"email": f"ghost_{uuid.uuid4().hex}@nowhere.com"}
        response = requests.post(f"{base_url}/auth/password-reset", json=payload)
        assert response.status_code in (200, 404), (
            f"Unexpected status for unknown email reset: {response.status_code}"
        )