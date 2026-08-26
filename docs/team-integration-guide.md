# RaktDaan Team Integration Guide

Welcome to the backend foundation built by **Member 1**. This guide explains how Team Members 2, 3, 4, and 5 can integrate their respective modules cleanly.

---

## Team Module Assignments
- **Member 1 (Current)**: Database Foundation, Registration, Donor Login, Admin Login, Authentication & Authorization, Security Infrastructure.
- **Member 2**: Home Page & Frontend UI Integration.
- **Member 3**: Donor Module & Donation Appointments.
- **Member 4**: Blood Inventory Management Module.
- **Member 5**: Blood Request & Admin Operations.

---

## How to Protect Routes in Other Modules

Import the authorization decorators from `app.auth.dependencies`:

```python
from flask import Blueprint, jsonify
from app.auth.dependencies import require_login, require_donor, require_admin, get_current_user

my_module_bp = Blueprint("my_module", __name__)

# Route accessible by any logged-in user
@my_module_bp.route("/my-profile", methods=["GET"])
@require_login
def my_profile():
    current_user = get_current_user()
    return jsonify(current_user.to_dict())

# Route accessible ONLY by Donors
@my_module_bp.route("/donor/appointments", methods=["GET"])
@require_donor
def donor_appointments():
    current_user = get_current_user()
    return jsonify({"donor_id": current_user.donor_profile.id})

# Route accessible ONLY by Admins
@my_module_bp.route("/admin/manage-inventory", methods=["POST"])
@require_admin
def admin_inventory():
    current_user = get_current_user()
    return jsonify({"admin": current_user.email})
```

---

## How to Define New Database Models

Import `db` and `BaseModelMixin` from `app.database`:

```python
from app.database.connection import db
from app.database.base import BaseModelMixin

class MemberModel(db.Model, BaseModelMixin):
    __tablename__ = "member_table_name"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    details = db.Column(db.String(255), nullable=False)
```
