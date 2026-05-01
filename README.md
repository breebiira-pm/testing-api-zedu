# Zedu API Automation

Python-based API test automation project built against the [Zedu platform](https://zedu.chat/) using **Pytest** and **Requests**.

This project was built for Stage 3 of the QA Engineering Track and demonstrates:
- Structured API test automation
- Dynamic authentication token handling (no hardcoded tokens)
- Positive, negative, and edge case test coverage (25+ tests)
- Clean separation of login logic, fixtures, and test files
- Environment variable management via `.env`

---

## Project Structure

```
zedu-api-automation/
│
├── tests/
│   ├── test_auth.py         # Register, login, logout, password reset
│   ├── test_users.py        # /users/me, /users/{id}, organisations, preferences
│   ├── test_channels.py     # Create, list, get, users, org channels
│   └── test_health.py       # Profile, presence, media preferences
│
├── utils/
│   └── auth.py              # Reusable login function — returns token/headers
│
├── conftest.py              # Shared Pytest fixtures (token, headers, org_id)
├── .env.example             # Environment variable template
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Prerequisites

- Python **3.9+**
- pip

---

## Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/testing-api-zedu.git
cd testing-api-zedu
```

### 2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Create your `.env` file

Copy the example file and fill in your credentials:

```bash
cp .env.example .env
```

Open `.env` and set:
```
BASE_URL=https://api.zedu.chat/api/v1
TEST_EMAIL=your_email@example.com
TEST_PASSWORD=your_password_here
TEST_ORG_ID=your_organisation_id_here
```

> Your `.env` file is listed in `.gitignore` and will NOT be committed to GitHub.

---

## Running the Tests

### Run the full test suite
```bash
pytest
```

### Run with verbose output
```bash
pytest -v
```

### Run a single test file
```bash
pytest tests/test_auth.py -v
pytest tests/test_users.py -v
pytest tests/test_channels.py -v
pytest tests/test_health.py -v
```

### Generate an HTML report
```bash
pytest --html=reports/report.html --self-contained-html
```

---

## Test File Coverage

| File | Endpoints Tested | What It Covers |
|---|---|---|
| `test_auth.py` | `/auth/register`, `/auth/login`, `/auth/logout`, `/auth/password-reset` | Registration, login (positive + negative), logout, password reset, edge cases (SQL injection, long passwords, whitespace) |
| `test_users.py` | `/users/me`, `/users/{id}`, `/users/organisations`, `/users/notification-preferences` | Current user fetch, user by ID, organisations list, preferences update, unauthenticated access |
| `test_channels.py` | `/channels`, `/channels/{id}/`, `/channels/{id}/users`, `/channels/{id}/num-users`, `/organisations/{orgId}/channels` | Channel creation, listing, retrieval, user count, org channels, unauthenticated access, edge case names |
| `test_health.py` | `/profile`, `/profile/{user_id}`, `/profile/presence`, `/users/media-preferences` | Profile get/update, presence status, media preferences, invalid tokens, long inputs |

---

## Authentication Design

- Login logic lives **only** in `utils/auth.py`
- `conftest.py` exposes a session-scoped `auth_token` fixture — login happens **once** per test run
- All test files consume `auth_headers` from the fixture — **no token is hardcoded anywhere**
- Negative tests that need to test bad tokens construct them inline without calling login

---

## Environment Variables

| Variable | Description |
|---|---|
| `BASE_URL` | Zedu API base URL (default: `https://api.zedu.chat/api/v1`) |
| `TEST_EMAIL` | Registered Zedu account email |
| `TEST_PASSWORD` | Registered Zedu account password |
| `TEST_ORG_ID` | Your organisation's ID in Zedu |