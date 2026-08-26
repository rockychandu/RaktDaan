# RaktDaan Security Policy & Cryptographic Standards

## Overview
This document outlines the security architecture, encryption standards, authentication flow, and rate limiting rules enforced by **Member 1**.

---

## 1. Password Storage & Complexity Policy
- **Hashing Algorithm**: PBKDF2 / scrypt / bcrypt with salt via `werkzeug.security`.
- **Plain-text Prohibition**: Plain-text passwords are NEVER stored in the database or included in API logs/responses.
- **Complexity Requirements**:
  - Minimum Length: 8 characters.
  - Required Character Sets: Uppercase (`A-Z`), Lowercase (`a-z`), Numeric (`0-9`), Special Character (`!@#$%^&*`).
  - Entropy Threshold: Minimum 30.0 bits of Shannon Entropy.
  - Common Password Blacklist: Reject top guessable passwords (`password123`, `admin123`, etc.).

---

## 2. PII Field-Level Encryption
Sensitive Personally Identifiable Information (PII) is encrypted before database persistence using AES-256 Fernet/XOR stream ciphers:
- Encrypted Columns: `donor_profiles.address_encrypted`, `donor_profiles.emergency_contact_encrypted`, `donor_emergency_contacts.phone_encrypted`.
- Ciphertext Prefix: Encrypted fields are prefixed with `ENC:` to distinguish them from unencrypted legacy data.

---

## 3. JWT Token Security & Session Management
- **Token Signature**: HMAC-SHA256 (`HS256`) using server `SECRET_KEY`.
- **Token Payloads**: Contains non-sensitive claims (`sub` [user_id], `role`, `email`, `jti`, `exp`, `iat`). Sensitive data (password hashes, emergency contacts) is omitted.
- **Token Expiration**: Access Tokens expire in 60 minutes. Refresh Tokens expire in 7 days.
- **Revocation Blacklist**: In-memory and DB tracking (`user_sessions.is_active`) invalidates tokens upon logout.

---

## 4. Rate Limiting & Brute-Force Protection
- Sliding window rate limiting applies to sensitive endpoints:
  - `POST /api/v1/auth/register`: 10 requests per minute per IP.
  - `POST /api/v1/auth/donor/login`: 15 requests per minute per IP.
  - `POST /api/v1/auth/admin/login`: 5 requests per minute per IP.
- Account Lockout: 5 consecutive failed login attempts lock the user account for 15 minutes (`users.locked_until`).
