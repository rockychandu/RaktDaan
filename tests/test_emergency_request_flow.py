"""
Automated Integration Test Suite for End-to-End Emergency Request Management Flow.
"""

from app.main import create_app
from app.database.connection import db
from app.services.emergency_request_service import EmergencyRequestService
from app.config import TestingConfig


def test_emergency_request_end_to_end_flow():
    app = create_app(TestingConfig)
    with app.app_context():
        db.create_all()

        # 1. Create Emergency Request from API
        with app.test_client() as client:
            payload = {
                "requester_name": "Dr. Sunita Rao",
                "contact_number": "9876543210",
                "patient_name": "Anil Verma",
                "patient_age": 42,
                "blood_group": "AB-",
                "units_required": 3,
                "hospital_name": "Apex City Hospital",
                "hospital_location": "South Zone, Delhi",
                "urgency_level": "STAT",
                "required_datetime": "2026-08-28 10:00 AM",
                "additional_reason": "Acute surgical trauma hemorrhage"
            }

            res = client.post("/api/emergency-requests", json=payload)
            assert res.status_code == 201
            res_data = res.get_json()
            assert res_data["status"] == "success"
            assert "ER-" in res_data["request_code"]
            req_code = res_data["request_code"]

            # 2. Get Requests via Admin API
            admin_res = client.get("/api/admin/emergency-requests")
            assert admin_res.status_code == 200
            admin_data = admin_res.get_json()
            assert admin_data["count"] >= 1
            matched = [r for r in admin_data["data"] if r["request_code"] == req_code]
            assert len(matched) == 1
            assert matched[0]["patient_name"] == "Anil Verma"
            assert matched[0]["urgency_level"] == "STAT"

            # 3. Get Requests via Donor API
            donor_res = client.get("/api/donor/emergency-requests?blood_group=AB-")
            assert donor_res.status_code == 200
            donor_data = donor_res.get_json()
            assert donor_data["count"] >= 1

            # 4. Donor Responds "I CAN DONATE"
            resp_payload = {
                "donor_name": "Rajesh Kumar",
                "donor_phone": "9988776655",
                "donor_blood_group": "AB-",
                "notes": "Available to donate immediately"
            }
            resp_res = client.post(f"/api/emergency-requests/{req_code}/respond", json=resp_payload)
            assert resp_res.status_code == 200
            assert resp_res.get_json()["status"] == "success"

            # 5. Admin updates status to APPROVED / ACTIVE
            status_res = client.put(f"/api/emergency-requests/{req_code}/status", json={"status": "APPROVED"})
            assert status_res.status_code == 200
            assert status_res.get_json()["data"]["status"] == "APPROVED"

            # 6. Verify Admin details endpoint shows donor response
            details_res = client.get(f"/api/emergency-requests/{req_code}")
            assert details_res.status_code == 200
            details_data = details_res.get_json()["data"]
            assert len(details_data["donor_responses"]) >= 1
            assert details_data["donor_responses"][0]["donor_name"] == "Rajesh Kumar"
