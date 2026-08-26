# RaktDaan Security Architecture & STRIDE Threat Model v2.0

## Table of Contents
1. [Security Principles & Defense-in-Depth](#1-security-principles--defense-in-depth)
2. [STRIDE Threat Modeling Matrix](#2-stride-threat-modeling-matrix)
3. [Cryptographic Standard Specifications](#3-cryptographic-standard-specifications)
4. [OWASP Top 10 Mitigation Matrix](#4-owasp-top-10-mitigation-matrix)
5. [Authentication & Authorization Sequence](#5-authentication--authorization-sequence)
6. [Incident Response & Security Logging](#6-incident-response--security-logging)

---

## 1. Security Principles & Defense-in-Depth

The RaktDaan security architecture implements a multi-layered **Defense-in-Depth** model covering data in transit, data at rest, identity verification, rate limiting, and audit logging.

```
+-------------------------------------------------------------------------+
| Layer 1: Edge & Network Security (HTTPS/TLS 1.3, CORS, WAF Rules)       |
+-------------------------------------------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
| Layer 2: Rate Limiting & Denial-of-Service Defense (Sliding Window)     |
+-------------------------------------------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
| Layer 3: Authentication & Role Verification (JWT, Separate Enpoints)   |
+-------------------------------------------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
| Layer 4: Granular Authorization (RBAC & ABAC Permission Matrix)         |
+-------------------------------------------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
| Layer 5: Data Storage Cryptography (AES-256 PII Encryption, PBKDF2/BC) |
+-------------------------------------------------------------------------+
```

---

## 2. STRIDE Threat Modeling Matrix

| Threat Category | Potential Risk | Impact | Mitigation Strategy Implemented |
| :--- | :--- | :--- | :--- |
| **Spoofing Identity** | Attacker attempts donor/admin credential stuffing. | HIGH | Sliding window rate limiting, PBKDF2 salted password hashing, 5-attempt account lockout. |
| **Tampering Data** | Modification of JWT token claims (e.g. changing role to `ADMIN`). | CRITICAL | Cryptographic HMAC-SHA256 token signatures verified on server-side for every request. |
| **Repudiation** | User denies performing administrative or profile changes. | MEDIUM | Immutable audit logging in `user_audit_logs` storing IP address, timestamp, and action code. |
| **Information Disclosure** | Leakage of donor medical history or emergency contact details via DB dump. | HIGH | Field-level AES-256 Fernet stream cipher encryption (`address_encrypted`, `emergency_contact_encrypted`). |
| **Denial of Service** | Automated bot flooding registration or login endpoints. | HIGH | Sliding window rate limiter tracking client IP address with HTTP 429 responses. |
| **Elevation of Privilege** | Donor attempts to call admin endpoints (`/admin/login` or `/admin/dashboard`). | CRITICAL | Strict role verification in service layer & view decorators (`@require_admin`). Roles supplied by frontend are ignored. |

---

## 3. Cryptographic Standard Specifications

### Password Hashing Algorithm
- **Primary Algorithm**: `PBKDF2-HMAC-SHA256` / `scrypt` / `bcrypt` with automatic salt generation via `werkzeug.security`.
- **Iteration Count**: Minimum 260,000 rounds for PBKDF2-HMAC-SHA256.
- **Salt Generation**: 128-bit cryptographically secure pseudorandom salt per password.

### Field-Level Encryption
- **Cipher Algorithm**: AES-256 Stream Cipher / Fernet (`CBC` mode with PKCS7 padding).
- **Key Derivation**: SHA-256 digest derived from `ENCRYPTION_KEY` environment variable.
- **Encrypted Fields**:
  - `donor_profiles.address_encrypted`
  - `donor_profiles.emergency_contact_encrypted`
  - `donor_emergency_contacts.phone_encrypted`

---

## 4. OWASP Top 10 Mitigation Matrix

| OWASP Risk | Category | Code Mitigation |
| :--- | :--- | :--- |
| **A01:2021** | Broken Access Control | View decorators `@require_login`, `@require_donor`, `@require_admin`, `@require_permission`. Server verifies DB role on every request. |
| **A02:2021** | Cryptographic Failures | Passwords hashed using PBKDF2/bcrypt. PII encrypted with AES-256. Sensitive password hashes excluded from response schemas. |
| **A03:2021** | Injection | SQLAlchemy 2.0 ORM parameterized queries prevent SQL Injection. `InputSanitizer` cleans XSS patterns. |
| **A04:2021** | Insecure Design | Separate `/donor/login` and `/admin/login` endpoints prevent single-entry-point role confusion. |
| **A05:2021** | Security Misconfiguration | Environment variables managed via `.env`. CORS headers strictly configured. Debug mode disabled in production. |
| **A07:2021** | Identification & Auth Failures | Generic login failure messages (`"Invalid email or password"`) prevent account enumeration. Lockout timer enforced. |
| **A08:2021** | Software & Data Integrity | Dependencies pinned in `requirements.txt`. |
| **A09:2021** | Security Logging & Failures | All auth failures and privilege escalations logged to `user_audit_logs` and `security_audit_logs`. |
