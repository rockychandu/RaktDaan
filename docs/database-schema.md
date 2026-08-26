# RaktDaan Blood Bank Management System - Database Schema Documentation

## Overview
This document specifies the database foundation designed by **Member 1** for the RaktDaan Blood Bank Management System. It serves as the common database and ORM contract for all 5 team members.

---

## Entity Relationship Diagram (ERD)

```
+------------------------------------+          +------------------------------------+
|               USERS                |          |           DONOR_PROFILES           |
+------------------------------------+          +------------------------------------+
| PK  id             INTEGER         |<--------1| PK  id                 INTEGER     |
| UK  email          VARCHAR(150)    |  (1-to-1)| FK  user_id            INTEGER (UK)|
|     name           VARCHAR(100)    |          |     date_of_birth      DATE        |
|     password_hash  VARCHAR(255)    |          |     gender             VARCHAR(20) |
|     role           VARCHAR(20)     |          |     blood_group        VARCHAR(10) |
|     phone          VARCHAR(20)     |          |     address            VARCHAR(255)|
|     status         VARCHAR(20)     |          |     city               VARCHAR(100)|
|     created_at     TIMESTAMP       |          |     state              VARCHAR(100)|
|     updated_at     TIMESTAMP       |          |     emergency_contact  VARCHAR(20) |
+------------------------------------+          |     created_at         TIMESTAMP   |
                                                |     updated_at         TIMESTAMP   |
                                                +------------------------------------+
```

---

## Data Dictionary

### 1. `users` Table
Stores base credentials, roles, and status for all system accounts (Donors & Admins).

| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | `PRIMARY KEY`, `AUTOINCREMENT` | Unique identifier |
| `name` | `VARCHAR(100)` | `NOT NULL` | User full name |
| `email` | `VARCHAR(150)` | `UNIQUE`, `NOT NULL`, `INDEX` | Account email (lowercase) |
| `password_hash` | `VARCHAR(255)` | `NOT NULL` | Secure bcrypt/pbkdf2 password hash |
| `role` | `VARCHAR(20)` | `NOT NULL`, Default: `'DONOR'` | Role enum (`DONOR`, `ADMIN`) |
| `phone` | `VARCHAR(20)` | `NOT NULL` | Contact phone number |
| `status` | `VARCHAR(20)` | `NOT NULL`, Default: `'ACTIVE'` | Account status (`ACTIVE`, `INACTIVE`) |
| `created_at` | `TIMESTAMP` | `NOT NULL`, Default: `UTC NOW` | Creation timestamp |
| `updated_at` | `TIMESTAMP` | `NOT NULL`, Default: `UTC NOW` | Last update timestamp |

---

### 2. `donor_profiles` Table
Stores extended donor information. Linked 1-to-1 with the `users` table.

| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | `PRIMARY KEY`, `AUTOINCREMENT` | Profile identifier |
| `user_id` | `INTEGER` | `FOREIGN KEY(users.id)`, `UNIQUE`, `NOT NULL` | Foreign key referencing `users.id` with `CASCADE DELETE` |
| `date_of_birth` | `DATE` | `NOT NULL` | Date of birth (YYYY-MM-DD) |
| `gender` | `VARCHAR(20)` | `NOT NULL` | Gender (`Male`, `Female`, `Other`) |
| `blood_group` | `VARCHAR(10)` | `NOT NULL` | Blood group (`A+`, `A-`, `B+`, `B-`, `AB+`, `AB-`, `O+`, `O-`) |
| `address` | `VARCHAR(255)` | `NOT NULL` | Street address |
| `city` | `VARCHAR(100)` | `NOT NULL` | City |
| `state` | `VARCHAR(100)` | `NOT NULL` | State |
| `emergency_contact` | `VARCHAR(20)` | `NOT NULL` | Emergency contact phone |
| `created_at` | `TIMESTAMP` | `NOT NULL`, Default: `UTC NOW` | Profile creation timestamp |
| `updated_at` | `TIMESTAMP` | `NOT NULL`, Default: `UTC NOW` | Profile update timestamp |

---

## Enumerated Values

### User Roles (`UserRole`)
- `DONOR`: Standard donor user account.
- `ADMIN`: System administrator account.
- *Arbitrary role values are strictly prohibited.*

### User Status (`UserStatus`)
- `ACTIVE`: Normal operating state.
- `INACTIVE`: Suspended or deactivated account.

### Blood Groups (`BloodGroup`)
- `A+`, `A-`, `B+`, `B-`, `AB+`, `AB-`, `O+`, `O-`

---

## Schema Extension Guide for Team Members

Other team members can easily extend the database without altering core authentication:

### Member 3 (Donor Donation Module)
Import `db` and reference `User.id` or `DonorProfile.id`:
```python
from app.database.connection import db

class Donation(db.Model):
    __tablename__ = "donations"
    id = db.Column(db.Integer, primary_key=True)
    donor_id = db.Column(db.Integer, db.ForeignKey("donor_profiles.id"), nullable=False)
    donation_date = db.Column(db.Date, nullable=False)
    units_ml = db.Column(db.Integer, nullable=False, default=450)
    status = db.Column(db.String(20), default="COMPLETED")
```

### Member 4 (Blood Inventory Module)
```python
from app.database.connection import db

class BloodInventory(db.Model):
    __tablename__ = "blood_inventory"
    id = db.Column(db.Integer, primary_key=True)
    blood_group = db.Column(db.String(10), nullable=False)
    units_available = db.Column(db.Integer, nullable=False, default=0)
    last_updated = db.Column(db.DateTime, default=db.func.now())
```

### Member 5 (Blood Request & Admin Module)
```python
from app.database.connection import db

class BloodRequest(db.Model):
    __tablename__ = "blood_requests"
    id = db.Column(db.Integer, primary_key=True)
    requester_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    blood_group = db.Column(db.String(10), nullable=False)
    units_needed = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default="PENDING") # PENDING, APPROVED, REJECTED
```
