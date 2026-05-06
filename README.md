# Zedu API Automation

![CI](https://github.com/breebiira-pm/testing-api-zedu/actions/workflows/ci.yml/badge.svg)

Python-based API test automation project built against the [Zedu platform](https://zedu.chat/) using **Pytest** and **Requests**.

Built for Stage 3 and Stage 4 of the QA Engineering Track.

---

## Project Structure

```
zedu-api-automation/
│
├── .github/
│   └── workflows/
│       └── ci.yml           # GitHub Actions CI pipeline
│
├── tests/
│   ├── test_auth.py         # Register, login, logout, password reset
│   ├── test_users.py        # /users/me, /users/{id}, organisations, preferences
│   ├── test_channels.py     # Create, list, get, users, org channels
│   └── test_health.py       # Profile, presence, media preferences
│
├── utils/
│   └── auth.py              # Reusable login function
│
├── conftest.py              # Shared Pytest fixtures
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
git clone https://github.com/breebiira-pm/testing-api-zedu.git
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
```bash
cp .env.example .env
```

Fill in your real values:
```
BASE_URL=https://api.zedu.chat/api/v1
TEST_EMAIL=your_email@example.com
TEST_PASSWORD=your_password_here
TEST_ORG_ID=your_organisation_slug_here
LOGIN_WRONG_PASSWORD=WrongPassword999!
LOGIN_BAD_EMAIL=ghost_user@nowhere.com
```

---

## Running the Tests

```bash
pytest -v
```

```bash
pytest --junitxml=report.xml
```

```bash
pytest --html=reports/report.html --self-contained-html
```

---

## CI/CD Pipeline

This project uses **GitHub Actions** for continuous integration.

The pipeline triggers automatically on every push to `main` and on every pull request.

### Pipeline Steps
1. Checkout code
2. Set up Python 3.11
3. Install dependencies from `requirements.txt`
4. Run full test suite with `pytest -v --junitxml=report.xml`
5. Upload JUnit XML report as a downloadable artifact

The pipeline **fails** if any test fails. No tests are suppressed or skipped silently.

---

## Environment Variables

For local runs, variables are loaded from `.env`. For CI, they are stored as GitHub Secrets.

| Variable | Description |
|---|---|
| `BASE_URL` | Zedu API base URL |
| `TEST_EMAIL` | Registered Zedu account email |
| `TEST_PASSWORD` | Registered Zedu account password |
| `TEST_ORG_ID` | Organisation slug in Zedu |
| `LOGIN_WRONG_PASSWORD` | Wrong password for negative tests |
| `LOGIN_BAD_EMAIL` | Non-existent email for negative tests |

---

## Authentication Design

- Login logic lives only in `utils/auth.py`
- `conftest.py` logs in once and shares the token across all tests via session-scoped fixtures
- No tokens are hardcoded anywhere in the codebase
- The login process includes an org-switch step required by the Zedu API to activate the session