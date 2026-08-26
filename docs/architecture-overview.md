# RaktDaan Enterprise Architecture Overview

## Overview
The **RaktDaan Blood Bank Management System** backend is structured around a modular, domain-driven architecture designed to support scalable blood bank operations, high-security authentication, field-level PII encryption, and extensibility across 5 developer modules.

---

## Architectural Layers

```
+-----------------------------------------------------------------------+
|                            CLIENT API LAYER                           |
|      (Donor Routes, Admin Routes, Health Diagnostics, CORS)           |
+-----------------------------------------------------------------------+
                                   |
                                   v
+-----------------------------------------------------------------------+
|                         VALIDATION & RBAC LAYER                       |
|   (RegistrationValidator, LoginValidator, RBACPermissionMatrix, g)    |
+-----------------------------------------------------------------------+
                                   |
                                   v
+-----------------------------------------------------------------------+
|                         BUSINESS SERVICE LAYER                        |
|   (RegistrationService, AuthenticationService, TokenService)          |
+-----------------------------------------------------------------------+
                                   |
                                   v
+-----------------------------------------------------------------------+
|                    SECURITY & CRYPTOGRAPHY ENGINE                     |
| (PasswordPolicyEngine, JWTManager, FieldEncryptor, RateLimiter)       |
+-----------------------------------------------------------------------+
                                   |
                                   v
+-----------------------------------------------------------------------+
|                         DATABASE & ORM LAYER                          |
|    (SQLAlchemy 2.0, User, DonorProfile, BloodInventory, Base)         |
+-----------------------------------------------------------------------+
```

---

## Key Design Principles
1. **Domain-Driven Modular Design**: Authentication, Security, Database Models, and Utilities are cleanly separated into decoupled packages.
2. **Security-First**: Sensitive PII fields are encrypted at rest using AES-256 stream ciphers (`ENC:...`).
3. **Decoupled Roles**: Separate `/donor/login` and `/admin/login` endpoints prevent privilege escalation.
4. **Audit Trail**: All authentication events, password updates, and privilege checks are logged in `user_audit_logs` and `security_audit_logs`.
5. **Team Integration**: Core ORM models (`User`, `DonorProfile`, `BloodInventory`, `BloodBag`, `BloodRequest`) are exported centrally to allow Team Members 3, 4, and 5 to import them without modifying auth logic.
