# RaktDaan Enterprise API Specification v2.0

## Table of Contents
1. [Global API Standards](#1-global-api-standards)
2. [Authentication & Authorization Headers](#2-authentication--authorization-headers)
3. [Error Code Catalog](#3-error-code-catalog)
4. [Public Donor Registration API](#4-public-donor-registration-api)
5. [Donor Authentication API](#5-donor-authentication-api)
6. [Admin Authentication API](#6-admin-authentication-api)
7. [User Profile & Identity API](#7-user-profile--identity-api)
8. [Session & Token Management API](#8-session--token-management-api)
9. [Health & System Diagnostics API](#9-health--system-diagnostics-api)
10. [Frontend Integration Contract for Member 2](#10-frontend-integration-contract-for-member-2)

---

## 1. Global API Standards

The RaktDaan API strictly adheres to RESTful architectural principles. All API requests and responses utilize UTF-8 encoded JSON payload bodies.

- **Base URL**: `/api/v1`
- **Default Content-Type**: `application/json`
- **Date/Time Format**: ISO-8601 UTC string (`YYYY-MM-DDTHH:MM:SS.mmmmmm+00:00`)
- **HTTP Status Codes**:
  - `200 OK`: Request succeeded.
  - `201 Created`: Resource successfully created.
  - `400 Bad Request`: Malformed JSON syntax or bad client request.
  - `401 Unauthorized`: Missing, invalid, or expired authentication token.
  - `403 Forbidden`: Authenticated user lacks required role or permission.
  - `404 Not Found`: Requested endpoint or entity resource does not exist.
  - `422 Unprocessable Entity`: Input validation failure (field errors provided).
  - `423 Locked`: Account is locked due to security lockout policy.
  - `429 Too Many Requests`: Rate limit threshold exceeded.
  - `500 Internal Server Error`: Server exception encountered.

---

## 2. Authentication & Authorization Headers

All protected endpoints require the client to supply an HTTP `Authorization` header containing a valid JSON Web Token (JWT) formatted as a Bearer token:

```http
Authorization: Bearer <JWT_ACCESS_TOKEN>
```

### Access Token Claims Schema
```json
{
  "sub": "42",
  "role": "DONOR",
  "email": "donor@example.com",
  "jti": "access_42_1771999200",
  "type": "access",
  "iat": 1771999200,
  "exp": 1772002800
}
```

---

## 3. Error Code Catalog

| Error Code | HTTP Status | Description | Remediation |
| :--- | :--- | :--- | :--- |
| `ERR_VAL_INVALID_INPUT` | 422 | One or more input fields failed validation. | Inspect `detail` map and correct fields. |
| `ERR_VAL_DUPLICATE_EMAIL` | 422 | Email address is already registered. | Login or use a different email address. |
| `ERR_VAL_WEAK_PASSWORD` | 422 | Password failed complexity requirements. | Provide password matching security rules. |
| `ERR_AUTH_CREDENTIALS_INVALID` | 401 | Email or password incorrect. | Check credentials and retry. |
| `ERR_AUTH_ROLE_MISMATCH` | 401 | Account does not possess required role. | Use correct login endpoint for your account role. |
| `ERR_AUTH_TOKEN_EXPIRED` | 401 | JWT access token expired. | Perform token refresh or re-authenticate. |
| `ERR_AUTH_TOKEN_REVOKED` | 401 | JWT token was explicitly logged out. | Re-authenticate to obtain new token. |
| `ERR_AUTH_ACCOUNT_LOCKED` | 423 | Account locked due to repeated failed logins. | Wait for lockout timer to expire (15 mins). |
| `ERR_AUTH_ACCOUNT_INACTIVE` | 403 | Account has been suspended or deactivated. | Contact system administrator. |
| `ERR_PERM_INSUFFICIENT` | 403 | Role lacks specific permission. | Contact administrator for elevated access. |
| `ERR_RATE_LIMIT_EXCEEDED` | 429 | Client exceeded request rate limit. | Wait 60 seconds before making requests. |

---

## 4. Public Donor Registration API

### Request Specification
- **Endpoint**: `POST /api/v1/auth/register`
- **Authentication**: None (Public)
- **Rate Limit**: 10 requests per minute per IP

#### Request Payload
```json
{
  "name": "Aarav Sharma",
  "email": "aarav.sharma@example.com",
  "phone": "9876543210",
  "password": "Password123!",
  "confirm_password": "Password123!",
  "date_of_birth": "1996-08-20",
  "gender": "Male",
  "blood_group": "O+",
  "address": "402 Heights Boulevard, Bandra West",
  "city": "Mumbai",
  "state": "Maharashtra",
  "emergency_contact": "9876543211"
}
```

#### Field Rules & Restrictions
1. `name`: Required. String between 2 and 100 characters.
2. `email`: Required. Valid RFC 5322 email syntax. Case-insensitive lowercase. Must be unique in DB.
3. `phone`: Required. 10 to 15 numeric digits (optional leading `+`).
4. `password`: Required. Minimum 8 characters. Must contain >= 1 uppercase letter (`A-Z`), >= 1 lowercase letter (`a-z`), >= 1 digit (`0-9`), and >= 1 special character (`!@#$%^&*()_+-=[]{};':"|,.<>/?`). Minimum 30.0 bits Shannon entropy.
5. `confirm_password`: Required. Must exactly match `password`.
6. `date_of_birth`: Required. Format `YYYY-MM-DD`. Must be in past. Donor age must be >= 18 and <= 100 years.
7. `gender`: Required. Must be one of `['Male', 'Female', 'Other']`.
8. `blood_group`: Required. Must be one of `['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']`.
9. `address`: Required. Street address string (encrypted at rest with AES-256).
10. `city`: Required. City name string.
11. `state`: Required. State name string.
12. `emergency_contact`: Required. 10 to 15 numeric digits (encrypted at rest with AES-256).

#### Response Specifications

##### Success Response (`201 Created`)
```json
{
  "success": true,
  "message": "Donor registered successfully.",
  "data": {
    "id": 42,
    "name": "Aarav Sharma",
    "email": "aarav.sharma@example.com",
    "phone": "9876543210",
    "role": "DONOR",
    "status": "ACTIVE",
    "failed_login_attempts": 0,
    "last_login_at": null,
    "created_at": "2026-08-26T11:45:00.000000+00:00",
    "updated_at": "2026-08-26T11:45:00.000000+00:00",
    "donor_profile": {
      "id": 18,
      "user_id": 42,
      "date_of_birth": "1996-08-20",
      "gender": "Male",
      "blood_group": "O+",
      "address": "402 Heights Boulevard, Bandra West",
      "city": "Mumbai",
      "state": "Maharashtra",
      "emergency_contact": "9876543211",
      "eligibility_status": "ELIGIBLE",
      "last_donation_date": null,
      "created_at": "2026-08-26T11:45:00.000000+00:00",
      "updated_at": "2026-08-26T11:45:00.000000+00:00"
    }
  }
}
```

##### Validation Error Response (`422 Unprocessable Entity`)
```json
{
  "success": false,
  "message": "Validation failed for request data.",
  "detail": {
    "email": "Email is already registered. Please login or use a different email.",
    "password": "Password must contain at least one special character."
  }
}
```

---

## 5. Donor Authentication API

### Request Specification
- **Endpoint**: `POST /api/v1/auth/donor/login`
- **Authentication**: None (Public)
- **Rate Limit**: 15 requests per minute per IP

#### Request Payload
```json
{
  "email": "aarav.sharma@example.com",
  "password": "Password123!"
}
```

#### Response Specifications

##### Success Response (`200 OK`)
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "role": "DONOR",
  "user": {
    "id": 42,
    "name": "Aarav Sharma",
    "email": "aarav.sharma@example.com",
    "phone": "9876543210",
    "role": "DONOR",
    "status": "ACTIVE",
    "donor_profile": {
      "id": 18,
      "blood_group": "O+",
      "city": "Mumbai",
      "eligibility_status": "ELIGIBLE"
    }
  }
}
```

##### Failure Response (`401 Unauthorized`)
```json
{
  "success": false,
  "message": "Invalid email or password.",
  "detail": "Invalid email or password."
}
```

---

## 6. Admin Authentication API

### Request Specification
- **Endpoint**: `POST /api/v1/auth/admin/login`
- **Authentication**: None (Public)
- **Rate Limit**: 5 requests per minute per IP

#### Request Payload
```json
{
  "email": "admin@raktdaan.org",
  "password": "Admin@RaktDaan123"
}
```

#### Response Specifications

##### Success Response (`200 OK`)
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "role": "ADMIN",
  "user": {
    "id": 1,
    "name": "System Admin",
    "email": "admin@raktdaan.org",
    "phone": "9876543210",
    "role": "ADMIN",
    "status": "ACTIVE",
    "donor_profile": null
  }
}
```

##### Donor Account Rejection Response (`401 Unauthorized`)
```json
{
  "success": false,
  "message": "Unauthorized access. Account is not registered as admin.",
  "detail": "Unauthorized access. Account is not registered as admin."
}
```

---

## 7. User Profile & Identity API

### Request Specification
- **Endpoint**: `GET /api/v1/auth/me`
- **Authentication**: Required (`Authorization: Bearer <token>`)

#### Success Response (`200 OK`)
```json
{
  "id": 42,
  "name": "Aarav Sharma",
  "email": "aarav.sharma@example.com",
  "phone": "9876543210",
  "role": "DONOR",
  "status": "ACTIVE",
  "donor_profile": {
    "id": 18,
    "date_of_birth": "1996-08-20",
    "gender": "Male",
    "blood_group": "O+",
    "address": "402 Heights Boulevard, Bandra West",
    "city": "Mumbai",
    "state": "Maharashtra",
    "emergency_contact": "9876543211",
    "eligibility_status": "ELIGIBLE"
  }
}
```

---

## 8. Session & Token Management API

### Logout Endpoint
- **Endpoint**: `POST /api/v1/auth/logout`
- **Authentication**: Required (`Authorization: Bearer <token>`)

#### Success Response (`200 OK`)
```json
{
  "success": true,
  "message": "Successfully logged out user aarav.sharma@example.com.",
  "data": {}
}
```

---

## 9. Health & System Diagnostics API

### Health Check Endpoint
- **Endpoint**: `GET /health`
- **Authentication**: None (Public)

#### Success Response (`200 OK`)
```json
{
  "status": "online",
  "app_name": "RaktDaan Enterprise Blood Bank System",
  "version": "2.0.0",
  "environment": "development",
  "database": "healthy"
}
```

---

## 10. Frontend Integration Contract for Member 2

When Member 2 builds the home page UI buttons:

1. **`[ DONOR LOGIN ]` Button**:
   - Opens `/donor/login` route.
   - Submits `{ "email": "...", "password": "..." }` to `POST /api/v1/auth/donor/login`.
   - On success (`200 OK`), saves `access_token` into `localStorage.setItem('auth_token', res.access_token)` and redirects user to `/donor/dashboard`.

2. **`[ ADMIN LOGIN ]` Button**:
   - Opens `/admin/login` route.
   - Submits `{ "email": "...", "password": "..." }` to `POST /api/v1/auth/admin/login`.
   - On success (`200 OK`), saves `access_token` into `localStorage.setItem('auth_token', res.access_token)` and redirects user to `/admin/dashboard`.

3. **`[ REGISTER ]` Button**:
   - Opens donor registration form.
   - Submits 12 fields to `POST /api/v1/auth/register`.
   - On success (`201 Created`), displays a notification: *"Registration successful! Please login as a Donor."* and redirects to `/donor/login`.
