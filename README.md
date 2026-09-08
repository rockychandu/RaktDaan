# RaktDaan Blood Bank Management System (Member 1 Foundation)

Welcome to the backend foundation for **RaktDaan Blood Bank Management System**.
This repository contains the Database schema foundation, Donor Registration, Donor & Admin Authentication, and Role-Based Authorization built by **Member 1**.

---

## Technical Stack & Architecture

- **Backend Framework**: Python Flask (REST API)
- **Database & ORM**: SQLite (Development) / PostgreSQL (Production) + Flask-SQLAlchemy (SQLAlchemy 2.0 ORM)
- **Security & Hashing**: Secure password hashing (`werkzeug.security` / `bcrypt`), JWT tokens (`PyJWT`)
- **Testing**: `pytest` + `pytest-flask`
- **Environment**: Configured via `.env` file

---

## Directory Structure

```
RaktDaan1/
│
├── app/
│   ├── __init__.py
│   ├── main.py                     # Flask app factory & entry point
│   ├── config.py                   # App settings & env loading
│   │
│   ├── auth/                       # Auth module
│   │   ├── __init__.py
│   │   ├── routes.py               # Blueprint routes (/register, /donor/login, /admin/login, /logout, /me)
│   │   ├── services.py             # Business logic (register_donor, authenticate_user)
│   │   ├── dependencies.py         # Authorization decorators (@require_login, @require_donor, @require_admin)
│   │   └── validators.py           # Request validation logic
│   │
│   ├── database/                   # Database module
│   │   ├── __init__.py
│   │   ├── connection.py           # SQLAlchemy database instance
│   │   ├── models.py               # User and DonorProfile ORM models
│   │   └── seed.py                 # Admin account seed script
│   │
│   ├── users/                      # User domain models
│   │   ├── __init__.py
│   │   └── models.py               # Enums: UserRole (DONOR, ADMIN), UserStatus, BloodGroup
│   │
│   └── utils/                      # Helper utilities
│       ├── __init__.py
│       └── security.py             # Password hashing & JWT generation/decoding
│
├── tests/                          # 14 Pytest Test Cases
│   ├── conftest.py                 # In-memory DB setup fixture
│   ├── test_registration.py        # Donor registration validation tests
│   ├── test_donor_login.py         # Donor login tests
│   ├── test_admin_login.py         # Admin login tests
│   └── test_authorization.py      # Role authorization and route protection tests
│
├── docs/
│   ├── database-schema.md          # Comprehensive database documentation for team
│   └── authentication-api.md       # API endpoint specification
│
├── .env.example                    # Environment variable template
├── requirements.txt                # Python dependencies
└── README.md                       # Project instructions
```

## 📦 Dependency Manifests & Lockfiles

This repository includes fully pinned dependency manifests and lockfiles for reproducible builds across development and production environments:

- **Manifest Files**: `requirements.txt`, `package.json`
- **Lockfile Copies**: `requirements.lock`, `package-lock.json`

---

## Setup & Quickstart Instructions

### 1. Environment & Dependency Installation

#### Option A: Python Virtual Environment (Recommended)
Create a virtual environment and install pinned dependencies from `requirements.txt` or `requirements.lock`:
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1
# On Linux/macOS:
source venv/bin/activate

# Install dependencies using pinned lockfile (reproducible build)
pip install -r requirements.lock

# OR install from main manifest
pip install -r requirements.txt
```

#### Option B: NPM Lockfile Installation (Asset Build Tools)
```bash
npm install
```

### 2. Configure Environment Variables
Copy `example.env` to `.env`:
```bash
cp example.env .env
```

### 3. Run the Development Server
```bash
python -m app.main
```
The server will start at `http://127.0.0.1:5000/`.
Initial admin account (`admin@raktdaan.org`) will be automatically seeded into the database on startup.

---

## Running Automated Tests

Run the complete test suite covering all 14 authentication & authorization scenarios:
```bash
python -m pytest -v
```

---

## Guide for Team Members (Integration)

### Connecting to Database & Using Models
Team members (Member 3, 4, 5) can import `db`, `User`, and `DonorProfile` directly:
```python
from app.database import db, User, DonorProfile

# Create a new table referencing User
class MyModuleModel(db.Model):
    __tablename__ = "my_module_table"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
```

### Protecting Routes with Authorization Decorators
To restrict access to routes in other modules:
```python
from app.auth.dependencies import require_login, require_donor, require_admin, get_current_user

# Require logged in donor
@my_blueprint.route("/donor/action", methods=["POST"])
@require_donor
def donor_action():
    current_user = get_current_user()
    return f"Hello Donor {current_user.name}"

# Require logged in admin
@my_blueprint.route("/admin/action", methods=["POST"])
@require_admin
def admin_action():
    current_user = get_current_user()
    return f"Hello Admin {current_user.name}"
```
