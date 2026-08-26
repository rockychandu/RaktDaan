# RaktDaan Enterprise Database Dictionary & DDL Schema v2.0

## Table of Contents
1. [Database Architecture & Engine Specifications](#1-database-architecture--engine-specifications)
2. [Entity Relationship Map (ERM)](#2-entity-relationship-map-erm)
3. [Core Table Definitions](#3-core-table-definitions)
   - [users Table](#31-users-table)
   - [donor_profiles Table](#32-donor_profiles-table)
   - [user_sessions Table](#33-user_sessions-table)
   - [user_audit_logs Table](#34-user_audit_logs-table)
   - [password_histories Table](#35-password_histories-table)
   - [blood_inventory Table](#36-blood_inventory-table)
   - [blood_bags Table](#37-blood_bags-table)
   - [blood_requests Table](#38-blood_requests-table)
   - [blood_compatibility_matrices Table](#39-blood_compatibility_matrices-table)
4. [Complete ANSI SQL DDL Script](#4-complete-ansi-sql-ddl-script)
5. [Database Extension Rules for Team Members](#5-database-extension-rules-for-team-members)

---

## 1. Database Architecture & Engine Specifications

- **Supported DBMS Dialects**: SQLite 3 (Development/Testing), PostgreSQL 14+ (Production), MySQL 8.0+ (Enterprise Cloud)
- **ORM Mapping Framework**: SQLAlchemy 2.0 ORM with Flask-SQLAlchemy 3.1
- **Character Encoding**: UTF-8 (`utf8mb4` on MySQL / `UTF8` on PostgreSQL)
- **Timezone**: UTC (`TIMESTAMP WITH TIME ZONE`)
- **Naming Conventions**: `snake_case` for all table names and column identifiers

---

## 2. Entity Relationship Map (ERM)

```
                       +------------------------+
                       |         USERS          |
                       +------------------------+
                       | PK  id                 |
                       | UK  email              |
                       |     password_hash      |
                       |     role               |
                       |     status             |
                       +------------------------+
                                 |  |  |
            +--------------------+  |  +--------------------+
            | 1-to-1                | 1-to-N                | 1-to-N
            v                       v                       v
+------------------------+ +------------------------+ +------------------------+
|     DONOR_PROFILES     | |     USER_SESSIONS      | |    USER_AUDIT_LOGS     |
+------------------------+ +------------------------+ +------------------------+
| PK  id                 | | PK  id                 | | PK  id                 |
| FK  user_id (UK)       | | FK  user_id            | | FK  user_id            |
|     date_of_birth      | | UK  session_token_jti  | |     action_type        |
|     blood_group        | |     ip_address         | |     description        |
|     address_encrypted  | |     expires_at         | |     ip_address         |
|     eligibility_status | |     is_active          | |     created_at         |
+------------------------+ +------------------------+ +------------------------+
            |
            | 1-to-N
            v
+------------------------+          +------------------------+
|       BLOOD_BAGS       |          |    BLOOD_INVENTORY     |
+------------------------+          +------------------------+
| PK  id                 |          | PK  id                 |
| FK  donor_id           |          | UK  blood_group        |
|     bag_code (UK)      |          |     units_available    |
|     blood_group        |          |     units_reserved     |
|     collection_date    |          |     units_expired      |
|     expiry_date        |          +------------------------+
+------------------------+
```

---

## 3. Core Table Definitions

### 3.1 `users` Table
Primary entity table storing user credentials, role declarations, and security status.

| Column Identifier | Data Type | Nullable | Key / Constraint | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | `NO` | `PRIMARY KEY AUTOINCREMENT` | Internal user ID |
| `name` | `VARCHAR(100)` | `NO` | — | User full name |
| `email` | `VARCHAR(150)` | `NO` | `UNIQUE INDEX` | Primary login email address |
| `password_hash` | `VARCHAR(255)` | `NO` | — | PBKDF2/bcrypt salted hash |
| `role` | `VARCHAR(20)` | `NO` | `INDEX` | Account role (`DONOR`, `ADMIN`) |
| `phone` | `VARCHAR(20)` | `NO` | — | Phone contact number |
| `status` | `VARCHAR(20)` | `NO` | `INDEX` | Lifecycle status (`ACTIVE`, `LOCKED`) |
| `failed_login_attempts` | `INTEGER` | `NO` | Default: `0` | Counter for brute force lockout |
| `locked_until` | `TIMESTAMP` | `YES` | — | Security lockout expiration date |
| `last_login_at` | `TIMESTAMP` | `YES` | — | Timestamp of last successful login |
| `created_at` | `TIMESTAMP` | `NO` | Default: `UTC NOW` | Audit creation date |
| `updated_at` | `TIMESTAMP` | `NO` | Default: `UTC NOW` | Audit modification date |
| `is_deleted` | `BOOLEAN` | `NO` | Default: `FALSE`, `INDEX` | Soft delete flag |
| `deleted_at` | `TIMESTAMP` | `YES` | — | Soft delete timestamp |

---

### 3.2 `donor_profiles` Table
Extended donor profile table linked 1-to-1 with `users`. Contains encrypted PII columns.

| Column Identifier | Data Type | Nullable | Key / Constraint | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | `NO` | `PRIMARY KEY AUTOINCREMENT` | Profile ID |
| `user_id` | `INTEGER` | `NO` | `FOREIGN KEY (users.id) UNIQUE` | FK to `users` with `CASCADE DELETE` |
| `date_of_birth` | `DATE` | `NO` | — | Date of birth (YYYY-MM-DD) |
| `gender` | `VARCHAR(20)` | `NO` | — | Gender string (`Male`, `Female`, `Other`) |
| `blood_group` | `VARCHAR(10)` | `NO` | `INDEX` | Blood group (`A+`, `O-`, etc.) |
| `address_encrypted` | `VARCHAR(255)` | `NO` | — | AES-256 encrypted street address |
| `city` | `VARCHAR(100)` | `NO` | `INDEX` | City location |
| `state` | `VARCHAR(100)` | `NO` | `INDEX` | State location |
| `emergency_contact_encrypted`| `VARCHAR(255)`| `NO` | — | AES-256 encrypted contact phone |
| `eligibility_status` | `VARCHAR(30)` | `NO` | `INDEX` | Eligibility (`ELIGIBLE`, `INELIGIBLE`) |
| `last_donation_date` | `DATE` | `YES` | — | Last donation date |
| `created_at` | `TIMESTAMP` | `NO` | Default: `UTC NOW` | Profile creation date |
| `updated_at` | `TIMESTAMP` | `NO` | Default: `UTC NOW` | Profile update date |
| `is_deleted` | `BOOLEAN` | `NO` | Default: `FALSE` | Soft delete flag |

---

### 3.3 `user_sessions` Table
Session tracking table for JWT token revocation and active session audits.

| Column Identifier | Data Type | Nullable | Key / Constraint | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | `NO` | `PRIMARY KEY AUTOINCREMENT` | Session ID |
| `user_id` | `INTEGER` | `NO` | `FOREIGN KEY (users.id)` | FK referencing user |
| `session_token_jti` | `VARCHAR(255)` | `NO` | `UNIQUE INDEX` | Unique JWT JTI token string |
| `ip_address` | `VARCHAR(45)` | `YES` | — | IPv4 / IPv6 client IP address |
| `user_agent` | `VARCHAR(255)` | `YES` | — | Client browser / device string |
| `expires_at` | `TIMESTAMP` | `NO` | — | Session token expiration date |
| `is_active` | `BOOLEAN` | `NO` | Default: `TRUE` | Active state flag |

---

### 3.4 `user_audit_logs` Table
Audit trail logging all security events, authentication attempts, and profile modifications.

| Column Identifier | Data Type | Nullable | Key / Constraint | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | `NO` | `PRIMARY KEY AUTOINCREMENT` | Audit log ID |
| `user_id` | `INTEGER` | `YES` | `FOREIGN KEY (users.id)` | FK to user (if authenticated) |
| `action_type` | `VARCHAR(50)` | `NO` | `INDEX` | Audit action classification |
| `description` | `VARCHAR(255)` | `NO` | — | Human-readable event detail |
| `ip_address` | `VARCHAR(45)` | `YES` | — | Event originator IP address |
| `created_at` | `TIMESTAMP` | `NO` | Default: `UTC NOW` | Timestamp of event |

---

## 4. Complete ANSI SQL DDL Script

```sql
-- Database Schema for RaktDaan Blood Bank Management System

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'DONOR',
    phone VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    failed_login_attempts INTEGER NOT NULL DEFAULT 0,
    locked_until TIMESTAMP NULL,
    last_login_at TIMESTAMP NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN NOT NULL DEFAULT 0,
    deleted_at TIMESTAMP NULL
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_status ON users(status);

CREATE TABLE donor_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE,
    date_of_birth DATE NOT NULL,
    gender VARCHAR(20) NOT NULL,
    blood_group VARCHAR(10) NOT NULL,
    address_encrypted VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    emergency_contact_encrypted VARCHAR(255) NOT NULL,
    eligibility_status VARCHAR(30) NOT NULL DEFAULT 'ELIGIBLE',
    last_donation_date DATE NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN NOT NULL DEFAULT 0,
    deleted_at TIMESTAMP NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_donor_blood_group ON donor_profiles(blood_group);
CREATE INDEX idx_donor_city ON donor_profiles(city);
CREATE INDEX idx_donor_state ON donor_profiles(state);

CREATE TABLE user_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    session_token_jti VARCHAR(255) NOT NULL UNIQUE,
    ip_address VARCHAR(45) NULL,
    user_agent VARCHAR(255) NULL,
    expires_at TIMESTAMP NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN NOT NULL DEFAULT 0,
    deleted_at TIMESTAMP NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE user_audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NULL,
    action_type VARCHAR(50) NOT NULL,
    description VARCHAR(255) NOT NULL,
    ip_address VARCHAR(45) NULL,
    metadata_json TEXT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN NOT NULL DEFAULT 0,
    deleted_at TIMESTAMP NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE blood_inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    blood_group VARCHAR(10) NOT NULL UNIQUE,
    units_available INTEGER NOT NULL DEFAULT 0,
    units_reserved INTEGER NOT NULL DEFAULT 0,
    units_expired INTEGER NOT NULL DEFAULT 0,
    last_updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN NOT NULL DEFAULT 0,
    deleted_at TIMESTAMP NULL
);
```
