# RaktDaan Authentication & Authorization API Specification

## Overview
This API provides separate authentication flows for **Donors** and **Admins**, input validation, and role-based access control.

Base URL: `/api/v1/auth`

---

## Endpoint Summary

| Endpoint | Method | Access | Description |
| :--- | :--- | :--- | :--- |
| `/api/v1/auth/register` | `POST` | Public | Register a new donor account |
| `/api/v1/auth/donor/login` | `POST` | Public | Authenticate a donor account |
| `/api/v1/auth/admin/login` | `POST` | Public | Authenticate an admin account |
| `/api/v1/auth/logout` | `POST` | Authenticated | Log out current session |
| `/api/v1/auth/me` | `GET` | Authenticated | Get current authenticated user profile |
| `/api/v1/auth/donor/dashboard-data` | `GET` | Donor Only | Protected sample route for Donor Dashboard |
| `/api/v1/auth/admin/dashboard-data` | `GET` | Admin Only | Protected sample route for Admin Dashboard |

---

## Detailed Specifications

### 1. Donor Registration (`POST /api/v1/auth/register`)

**Headers:**
`Content-Type: application/json`

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john.doe@example.com",
  "phone": "9876543210",
  "password": "Password123!",
  "confirm_password": "Password123!",
  "date_of_birth": "1995-05-15",
  "gender": "Male",
  "blood_group": "O+",
  "address": "123 Main Street",
  "city": "Mumbai",
  "state": "Maharashtra",
  "emergency_contact": "9876543211"
}
```

**Validation Rules:**
- All 12 fields are required.
- `email`: Valid email syntax, unique in system.
- `phone` & `emergency_contact`: 10 to 15 digits.
- `password`: >= 8 chars, 1 uppercase, 1 lowercase, 1 number, 1 special character (`!@#$%^&*()_+-=[]{};':"|,.<>/?`).
- `confirm_password`: Must equal `password`.
- `date_of_birth`: YYYY-MM-DD, age >= 18.
- `blood_group`: Must be one of `['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']`.

**Success Response (`201 Created`):**
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john.doe@example.com",
  "phone": "9876543210",
  "role": "DONOR",
  "status": "ACTIVE",
  "donor_profile": {
    "id": 1,
    "user_id": 1,
    "date_of_birth": "1995-05-15",
    "gender": "Male",
    "blood_group": "O+",
    "address": "123 Main Street",
    "city": "Mumbai",
    "state": "Maharashtra",
    "emergency_contact": "9876543211"
  }
}
```

**Error Response (`422 Unprocessable Entity`):**
```json
{
  "detail": {
    "email": "Email is already registered. Please login or use a different email."
  }
}
```

---

### 2. Donor Login (`POST /api/v1/auth/donor/login`)

**Headers:**
`Content-Type: application/json`

**Request Body:**
```json
{
  "email": "john.doe@example.com",
  "password": "Password123!"
}
```

**Success Response (`200 OK`):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "role": "DONOR",
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "john.doe@example.com",
    "phone": "9876543210",
    "role": "DONOR",
    "status": "ACTIVE",
    "donor_profile": { ... }
  }
}
```

**Error Response (`401 Unauthorized`):**
```json
{
  "detail": "Invalid email or password."
}
```

---

### 3. Admin Login (`POST /api/v1/auth/admin/login`)

**Headers:**
`Content-Type: application/json`

**Request Body:**
```json
{
  "email": "admin@raktdaan.org",
  "password": "Admin@RaktDaan123"
}
```

**Success Response (`200 OK`):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "role": "ADMIN",
  "user": {
    "id": 1,
    "name": "System Admin",
    "email": "admin@raktdaan.org",
    "phone": "9876543210",
    "role": "ADMIN",
    "status": "ACTIVE"
  }
}
```

**Error Response (Donor attempting Admin Login - `401 Unauthorized`):**
```json
{
  "detail": "Unauthorized access. Account is not registered as admin."
}
```

---

### 4. Current User Profile (`GET /api/v1/auth/me`)

**Headers:**
`Authorization: Bearer <access_token>`

**Success Response (`200 OK`):**
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john.doe@example.com",
  "phone": "9876543210",
  "role": "DONOR",
  "status": "ACTIVE",
  "donor_profile": { ... }
}
```

---

### 5. Logout (`POST /api/v1/auth/logout`)

**Headers:**
`Authorization: Bearer <access_token>`

**Success Response (`200 OK`):**
```json
{
  "success": true,
  "message": "Successfully logged out user john.doe@example.com."
}
```

---

## Frontend Integration Guide for Member 2

When the user clicks frontend buttons:

- **`[ DONOR LOGIN ]`**: Opens `/donor/login` UI page. Sends payload to `POST /api/v1/auth/donor/login`. On success, stores token in `localStorage` or secure cookie and redirects to `/donor/dashboard`.
- **`[ ADMIN LOGIN ]`**: Opens `/admin/login` UI page. Sends payload to `POST /api/v1/auth/admin/login`. On success, stores token and redirects to `/admin/dashboard`.
- **`[ REGISTER ]`**: Opens donor registration form. Sends payload to `POST /api/v1/auth/register`. On success, prompts user to login.
