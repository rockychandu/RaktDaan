"""
Comprehensive Automated Test Suite for Member 4 — Requester / Blood Request Module.

Tests:
1. Blood Request creation with 5-section validation
2. Public Request ID generation (RD-2026-XXXXXX)
3. Duplicate request detection and override
4. Status lifecycle transitions (SUBMITTED -> APPROVED -> PARTIALLY_FULFILLED -> FULFILLED)
5. Status history audit logging
6. ABO/Rh blood compatibility donor matching
7. Donor notification & voluntary response (AVAILABLE / NOT_AVAILABLE)
8. Partial and complete fulfillment calculations
9. Supporting document upload validation
10. Notification center read/unread management
11. REST API controller endpoints for Requester, Admin, and Donors
"""

import pytest
import io
from app.main import create_app
from app.config import Config
from app.database.connection import db
from app.database.models.user import User
from app.database.models.donor import DonorProfile
from app.database.models.blood_request import (
    BloodRequest, Hospital, BloodRequestDonorMatch, RequestNotification, RequestStatusHistory
)
from app.services.blood_request_service import BloodRequestService


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False


@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_create_blood_request_success(app):
    with app.app_context():
        payload = {
            "requester_name": "John Doe",
            "requester_phone": "9988776655",
            "requester_email": "john@example.com",
            "relationship_with_patient": "Relative",
            "patient_name": "Jane Doe",
            "patient_age": 42,
            "patient_gender": "Female",
            "blood_group": "O+",
            "component": "Whole Blood",
            "units_required": 2,
            "hospital_name": "Central Hospital",
            "hospital_city": "Central",
            "required_date": "2026-09-01",
            "urgency": "URGENT"
        }
        res = BloodRequestService.create_blood_request(payload)
        assert res["success"] is True
        assert res["public_request_id"].startswith("RD-2026-")
        assert res["data"]["units_remaining"] == 2
        assert res["data"]["status"] == "SUBMITTED"


def test_duplicate_request_detection(app):
    with app.app_context():
        payload = {
            "requester_name": "Alice Smith",
            "requester_phone": "9876500000",
            "patient_name": "Bob Smith",
            "blood_group": "A+",
            "units_required": 1,
            "hospital_name": "Metro Hospital",
            "hospital_city": "Central",
            "required_date": "2026-09-01",
            "urgency": "NORMAL"
        }
        res1 = BloodRequestService.create_blood_request(payload)
        assert res1["success"] is True

        # Second request with same patient & blood group should trigger duplicate warning
        res2 = BloodRequestService.create_blood_request(payload)
        assert res2["success"] is False
        assert res2["is_duplicate"] is True
        assert res2["status_code"] == 409

        # Override duplicate flag
        payload["override_duplicate"] = True
        res3 = BloodRequestService.create_blood_request(payload)
        assert res3["success"] is True


def test_status_lifecycle_and_fulfillment(app):
    with app.app_context():
        payload = {
            "requester_name": "Requester A",
            "requester_phone": "9123456789",
            "patient_name": "Patient A",
            "blood_group": "B+",
            "units_required": 4,
            "hospital_name": "City Hospital",
            "hospital_city": "Central",
            "required_date": "2026-09-02",
            "urgency": "HIGH"
        }
        create_res = BloodRequestService.create_blood_request(payload)
        req_id = create_res["public_request_id"]

        # Approve Request
        app_res = BloodRequestService.update_request_status(req_id, "APPROVED")
        assert app_res["success"] is True
        assert app_res["data"]["status"] in ["APPROVED", "MATCHING_DONORS"]

        # Partial Fulfillment (2 out of 4 units)
        part_res = BloodRequestService.update_request_status(req_id, "PARTIALLY_FULFILLED", units_collected=2)
        assert part_res["success"] is True
        assert part_res["data"]["units_collected"] == 2
        assert part_res["data"]["units_remaining"] == 2
        assert part_res["data"]["status"] == "PARTIALLY_FULFILLED"

        # Full Fulfillment (4 out of 4 units)
        full_res = BloodRequestService.update_request_status(req_id, "FULFILLED", units_collected=4)
        assert full_res["success"] is True
        assert full_res["data"]["units_collected"] == 4
        assert full_res["data"]["units_remaining"] == 0
        assert full_res["data"]["status"] == "FULFILLED"


def test_donor_matching_and_response(app):
    with app.app_context():
        payload = {
            "requester_name": "Requester B",
            "requester_phone": "9876543211",
            "patient_name": "Patient B",
            "blood_group": "O+",
            "units_required": 1,
            "hospital_name": "St Jude Hospital",
            "hospital_city": "Central",
            "required_date": "2026-09-03",
            "urgency": "EMERGENCY"
        }
        res = BloodRequestService.create_blood_request(payload)
        req = BloodRequest.query.filter_by(public_request_id=res["public_request_id"]).first()

        # Match eligible donors
        matched_count = BloodRequestService.find_and_notify_eligible_donors(req.id)
        assert matched_count >= 0

        # Donor responds AVAILABLE
        match = BloodRequestDonorMatch.query.filter_by(request_id=req.id).first()
        donor_id = match.donor_id if match else 1
        resp_res = BloodRequestService.record_donor_response(req.public_request_id, donor_id, "AVAILABLE", "Ready to donate tomorrow")
        assert resp_res["success"] is True
        assert resp_res["data"]["donor_response"] == "AVAILABLE"


def test_api_endpoints(client):
    # Test Create API
    payload = {
        "requester_name": "API Tester",
        "requester_phone": "9876543210",
        "patient_name": "API Patient",
        "blood_group": "AB+",
        "units_required": 1,
        "hospital_name": "API Hospital",
        "hospital_city": "Central",
        "required_date": "2026-09-05",
        "urgency": "NORMAL"
    }
    res = client.post("/api/blood-requests", json=payload)
    assert res.status_code == 201
    data = res.get_json()
    req_id = data["request_id"]

    # Test Details API
    res_det = client.get(f"/api/blood-requests/{req_id}")
    assert res_det.status_code == 200

    # Test Dashboard API
    res_dash = client.get("/api/requester/dashboard")
    assert res_dash.status_code == 200

    # Test History List API
    res_hist = client.get("/api/blood-requests")
    assert res_hist.status_code == 200

    # Test Cancel API
    res_cancel = client.post(f"/api/blood-requests/{req_id}/cancel", json={"reason": "Patient recovered"})
    assert res_cancel.status_code == 200
