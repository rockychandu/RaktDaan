# RaktDaan — Requester / Blood Request Module Documentation (Member 4)

## Executive Overview
The **Requester / Blood Request Module** is Member 4's official responsibility within the **RaktDaan Blood Bank Management System**.
This module introduces an end-to-end, production-style workflow that enables patients, doctors, relatives, and hospitals to submit, track, manage, and fulfill verified blood requirements without breaking existing Member 1 (Auth & Database), Member 2 (Home Page & Frontend), or Member 3 (Donor Management) implementations.

---

## 1. Architectural Highlights & Principles
1. **Zero External API Dependency**: Runs on Python Flask enterprise backend with SQLite persistence via SQLAlchemy.
2. **Backward Compatibility Guarantee**: Reuses existing `User` model, authentication pipelines (`JWTManager`, `AuthenticationService`), database connection (`db`), theme styling (`theme.css`), and navbar layout without deleting, renaming, or breaking Member 1–3 code.
3. **Role Extension**: Integrates `UserRole.REQUESTER = "REQUESTER"` into system RBAC matrix without altering existing `DONOR` and `ADMIN` roles.
4. **Public Request ID Generator**: Generates human-readable, non-sequential unique identifiers formatted as `RD-2026-XXXXXX` (e.g. `RD-2026-000001`).
5. **ABO/Rh Donor Matching Engine**: Matches compatible voluntary donors using clinical red-cell compatibility rules without exposing sensitive patient medical records to donors.
6. **Partial & Complete Fulfillment Engine**: Tracks `units_required`, `units_collected`, and `units_remaining` dynamically with state transitions (`PARTIALLY_FULFILLED` → `FULFILLED`).
7. **Multi-Channel Notification Abstraction**: Implements `UnifiedNotificationService` supporting `InAppNotificationService`, `EmailNotificationService`, and `SMSNotificationService` provider interfaces.
8. **Audit Trail Logging**: Stores every status transition and administrative note in `RequestStatusHistory`.

---

## 2. File & Directory Structure

```
c:\RaktDaan-Member3\
├── app/
│   ├── database/
│   │   ├── models/
│   │   │   ├── blood_request.py         [NEW] (BloodRequest, Hospital, DonorMatch, Notification, History, Document)
│   │   │   ├── __init__.py              [MODIFIED] (Re-exported Member 4 models)
│   │   │   └── blood_bank.py            [MODIFIED] (Delegated BloodRequest to blood_request.py)
│   │   └── models.py                    [MODIFIED] (Delegated DonorProfile to donor.py)
│   ├── routes/
│   │   └── blood_request_routes.py      [NEW] (REST API Controller for Requester, Admin, Donor response)
│   ├── services/
│   │   ├── blood_request_service.py     [NEW] (Domain Service for Workflow, Matching, FSM & Audit)
│   │   └── notification_delivery_service.py [NEW] (Notification Abstraction: InApp, Email, SMS)
│   ├── templates/
│   │   ├── index.html                   [MODIFIED] (Added 'Request Blood' CTA beside 'Donate Blood')
│   │   ├── admin_dashboard.html         [MODIFIED] (Integrated Blood Requests Management Tab 14)
│   │   ├── donor_dashboard.html         [MODIFIED] (Integrated Voluntary Donor Response Action)
│   │   ├── request_blood.html           [NEW] (Interactive 5-Step Workflow Form + Review Summary)
│   │   ├── request_tracking.html        [NEW] (Visual Progress Timeline Tracker)
│   │   ├── request_history.html         [NEW] (Request History, Search, Filters & Pagination)
│   │   ├── requester_login.html         [NEW] (Requester Portal Login UI)
│   │   └── requester_register.html      [NEW] (Requester Portal Registration UI)
│   ├── auth/
│   │   └── routes/
│   │       └── ui_routes.py             [MODIFIED] (Registered Requester Web UI routes)
│   ├── users/
│   │   └── models.py                    [MODIFIED] (Added REQUESTER role & audit action types)
│   └── main.py                          [MODIFIED] (Registered blood_request_api_bp blueprint)
├── tests/
│   └── test_blood_request_module.py     [NEW] (Automated Test Suite for Member 4)
└── REQUESTER_MODULE.md                  [NEW] (This Documentation File)
```

---

## 3. Database Schema Design (`app/database/models/blood_request.py`)

### `BloodRequest` Table (`blood_requests`)
- `id`: Primary key integer
- `public_request_id`: String unique index (e.g. `RD-2026-000001`)
- `requester_id`: Foreign key to `users.id` (nullable for guest/public requests)
- `requester_name`, `requester_phone`, `requester_email`, `relationship_with_patient`
- `patient_name`, `patient_age`, `patient_gender`, `patient_identifier`, `medical_condition`
- `blood_group`, `component`, `units_required`, `units_collected`, `units_remaining`
- `hospital_id`, `hospital_name`, `hospital_city`, `hospital_address`, `department_ward`, `bed_number`
- `required_date`, `required_time`, `urgency` (`NORMAL`, `URGENT`, `EMERGENCY`, `CRITICAL`)
- `status`: `DRAFT`, `SUBMITTED`, `UNDER_REVIEW`, `VERIFIED`, `APPROVED`, `MATCHING_DONORS`, `DONOR_NOTIFIED`, `PARTIALLY_FULFILLED`, `FULFILLED`, `REJECTED`, `CANCELLED`, `EXPIRED`
- `created_at`, `updated_at`, `approved_at`, `fulfilled_at`, `cancelled_at`

### `Hospital` Table (`hospitals`)
- `id`, `name`, `registration_number`, `address`, `city`, `state`, `pincode`, `phone`, `email`, `verification_status`

### `BloodRequestDonorMatch` Table (`blood_request_donor_matches`)
- `id`, `request_id`, `donor_id`, `match_reason`, `notification_status`, `donor_response` (`PENDING`, `AVAILABLE`, `NOT_AVAILABLE`), `responded_at`

### `RequestNotification` Table (`request_notifications`)
- `id`, `user_id`, `request_id`, `type`, `title`, `message`, `priority`, `is_read`, `created_at`, `read_at`

### `RequestStatusHistory` Table (`request_status_histories`)
- `id`, `request_id`, `old_status`, `new_status`, `changed_by`, `note`, `created_at`

### `RequestDocument` Table (`request_documents`)
- `id`, `request_id`, `document_type`, `file_path`, `file_name`, `file_size`, `mime_type`, `uploaded_by`, `created_at`

---

## 4. REST API Endpoint Reference

| HTTP Method | Endpoint | Access Role | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/blood-requests` | Public / Requester | Submits 5-step blood request & runs duplicate check |
| `GET` | `/api/blood-requests` | All / Public | Lists requests with search, filters & pagination |
| `GET` | `/api/blood-requests/<req_id>` | All / Public | Fetches complete request details & tracking timeline |
| `PUT/PATCH` | `/api/blood-requests/<req_id>` | Requester / Admin | Edits active blood request details |
| `POST` | `/api/blood-requests/<req_id>/cancel` | Requester / Admin | Cancels blood request with reason |
| `GET` | `/api/requester/dashboard` | Requester | Fetches dashboard metrics & recent requests |
| `GET` | `/api/admin/blood-requests` | Admin | Admin view of all requests & fulfillment metrics |
| `PATCH` | `/api/admin/blood-requests/<req_id>/status` | Admin | Updates status, units collected, and audit notes |
| `POST` | `/api/admin/blood-requests/<req_id>/approve` | Admin | Approves request & triggers donor matching |
| `POST` | `/api/admin/blood-requests/<req_id>/reject` | Admin | Rejects request with rationale |
| `GET` | `/api/blood-requests/<req_id>/eligible-donors` | Admin / System | Identifies compatible voluntary donors |
| `POST` | `/api/blood-requests/<req_id>/donor-response` | Donor | Records donor response (`AVAILABLE` / `NOT_AVAILABLE`) |
| `GET` | `/api/notifications` | User | Fetches user notifications with unread count |
| `PATCH` | `/api/notifications/read-all` | User | Marks all notifications as read |
| `POST` | `/api/blood-requests/<req_id>/documents` | Requester / Admin | Uploads supporting clinical document |

---

## 5. End-to-End Request Blood Workflow Scenario

```
Home Page (Click [ 🩸 Request Blood ])
  │
  ▼
Request Blood Form (/request-blood)
  ├── Section A: Requester Details (Name, Phone, Email, Relation, Address, City)
  ├── Section B: Patient Details (Name, Age, Gender, Blood Group, Component, Units, Doctor)
  ├── Section C: Hospital Details (Hospital Name, City, Address, Ward/Bed Number)
  ├── Section D: Urgency & Priority (NORMAL, URGENT, EMERGENCY, CRITICAL + Optional Document Upload)
  └── Section E: Review & Final Submission
  │
  ▼
Submit Blood Request (POST /api/blood-requests)
  ├── Backend validates input (mobile, email, units > 0, valid blood group)
  ├── Runs duplicate request check (48-hr window for same patient/phone)
  ├── Generates Unique Request ID: RD-2026-000001
  ├── Saves request & audit history (Status: SUBMITTED)
  └── Creates System Alert Notification for Admin Portal
  │
  ▼
Admin Portal Review & Donor Matching
  ├── Admin views request in Tab 14 ("Blood Requests")
  ├── Clicks [ Approve ]: Status changes to APPROVED -> MATCHING_DONORS
  ├── System queries ABO/Rh compatible eligible donors in same city
  └── Dispatches non-sensitive notifications to eligible donors
  │
  ▼
Donor Mobile / Portal Response
  ├── Matched Donors see alert: "Urgent Blood Request RD-2026-000001 (O+ Needed at City Hospital)"
  └── Donor clicks [ I CAN DONATE ]: Response stored as AVAILABLE
  │
  ▼
Fulfillment & Tracking
  ├── Requester tracks live progress on Visual Timeline (/request-tracking/RD-2026-000001)
  ├── Admin updates collected units (e.g. 2 of 2 units arranged)
  └── Status transitions to FULFILLED with audit trail record
```

---

## 6. Automated Testing Suite

Run Member 4 test suite with pytest:
```bash
python -m pytest tests/test_blood_request_module.py -v
```

### Verification Criteria Passed:
- 5-Section Blood Request validation & model creation
- Public Request ID (`RD-2026-XXXXXX`) format verification
- 48-Hour duplicate request detection & override handling
- Status lifecycle state machine & partial/full fulfillment calculations
- ABO/Rh blood compatibility donor matching engine
- Donor notification delivery & voluntary response tracking
- REST API controller endpoints for Requester, Admin, and Donors

---

## 7. Git Commit Instructions for Member 4

To commit only Member 4 changes to GitHub:

```bash
git checkout -b member4-requester-module

git add app/database/models/blood_request.py
git add app/services/blood_request_service.py
git add app/services/notification_delivery_service.py
git add app/routes/blood_request_routes.py
git add app/templates/request_blood.html
git add app/templates/request_tracking.html
git add app/templates/request_history.html
git add app/templates/requester_login.html
git add app/templates/requester_register.html
git add app/templates/requester_dashboard.html
git add app/templates/index.html
git add app/templates/admin_dashboard.html
git add app/templates/donor_dashboard.html
git add app/auth/routes/ui_routes.py
git add app/users/models.py
git add app/main.py
git add app/database/models/__init__.py
git add app/database/models.py
git add app/database/models/blood_bank.py
git add tests/test_blood_request_module.py
git add REQUESTER_MODULE.md

git commit -m "feat(requester): implement complete Blood Requester module for Member 4 without breaking team code"
```
