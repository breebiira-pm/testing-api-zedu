"""
debug.py - Run this to investigate the Zedu auth flow
Run with: python debug.py
"""
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL", "https://api.zedu.chat/api/v1")
EMAIL = os.getenv("TEST_EMAIL")
PASSWORD = os.getenv("TEST_PASSWORD")
ORG_SLUG = os.getenv("TEST_ORG_ID", "zedu-test-organisation")

print(f"EMAIL: {EMAIL}")
print(f"BASE_URL: {BASE_URL}")
print(f"ORG_SLUG: {ORG_SLUG}")
print()

# STEP 1: Login
print("=== STEP 1: LOGIN ===")
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={"email": EMAIL, "password": PASSWORD}
)
print(f"Status: {login_response.status_code}")
login_data = login_response.json()
print(f"Full response: {json.dumps(login_data, indent=2)[:800]}")

token = (
    login_data.get("data", {}).get("access_token")
    or login_data.get("access_token")
    or login_data.get("token")
    or login_data.get("data", {}).get("token")
)
print(f"\nToken: {token[:40] if token else 'NOT FOUND'}...")
print()

headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

# STEP 2: Test /users/me with login token
print("=== STEP 2: /users/me WITH LOGIN TOKEN ===")
me = requests.get(f"{BASE_URL}/users/me", headers=headers)
print(f"Status: {me.status_code}")
print(f"Response: {me.text[:300]}")
print()

# STEP 3: Switch org
print("=== STEP 3: SWITCH ORG ===")
switch = requests.get(f"{BASE_URL}/users/switch-org/{ORG_SLUG}", headers=headers)
print(f"Status: {switch.status_code}")
switch_data = switch.json()
print(f"Full response: {json.dumps(switch_data, indent=2)[:800]}")

new_token = (
    switch_data.get("data", {}).get("access_token")
    or switch_data.get("access_token")
    or switch_data.get("data", {}).get("token")
    or switch_data.get("token")
)
print(f"\nNew token from switch: {new_token[:40] if new_token else 'NOT FOUND - no new token'}")
print()

# STEP 4: Test /users/me after switch
print("=== STEP 4: /users/me AFTER SWITCH ===")
final_headers = {
    "Authorization": f"Bearer {new_token if new_token else token}",
    "Content-Type": "application/json"
}
me2 = requests.get(f"{BASE_URL}/users/me", headers=final_headers)
print(f"Status: {me2.status_code}")
print(f"Response: {me2.text[:300]}")
print()

# STEP 5: Try profile endpoint
print("=== STEP 5: /profile WITH FINAL TOKEN ===")
profile = requests.get(f"{BASE_URL}/profile", headers=final_headers)
print(f"Status: {profile.status_code}")
print(f"Response: {profile.text[:300]}")