import os
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL", "https://api.zedu.chat/api/v1")


def get_auth_token(email: str = None, password: str = None) -> str:
    url = f"{BASE_URL}/auth/login"
    payload = {
        "email": email or os.getenv("TEST_EMAIL"),
        "password": password or os.getenv("TEST_PASSWORD"),
    }
    response = requests.post(url, json=payload)
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

    return token


def get_auth_headers(email: str = None, password: str = None) -> dict:
    token = get_auth_token(email, password)
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}