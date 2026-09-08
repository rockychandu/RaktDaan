"""
Verification script: Submits an Emergency Request from Home Page API,
then verifies its persistence and availability in both Admin and Donor endpoints.
"""

from app.main import create_app
from app.database.connection import db

app = create_app()

with app.app_context():
    with app.test_client() as client:
        # 1. Home Page User submits Emergency Request
        home_payload = {
            "requester_name": "Amit Deshmukh",
            "contact_number": "9820011223",
            "patient_name": "Suresh Deshmukh",
            "patient_age": 55,
            "blood_group": "B+",
            "units_required": 2,
            "hospital_name": "Lilavati Hospital",
            "hospital_location": "Bandra West, Mumbai",
            "urgency_level": "STAT",
            "required_datetime": "2026-08-28 09:00 AM",
            "additional_reason": "Emergency cardiac bypass surgery"
        }

        print("\n--- 1. SUBMITTING EMERGENCY REQUEST FROM HOME PAGE ---")
        res = client.post("/api/emergency-requests", json=home_payload)
        data = res.get_json()
        print("Status Code:", res.status_code)
        print("Response:", data)
        req_code = data["request_code"]

        # 2. Verify availability in Admin Portal API
        print("\n--- 2. FETCHING FROM ADMIN PORTAL API ---")
        admin_res = client.get("/api/admin/emergency-requests")
        admin_data = admin_res.get_json()
        print("Admin Total Count:", admin_data["count"])
        matched_admin = [r for r in admin_data["data"] if r["request_code"] == req_code]
        print("Admin Found Request:", matched_admin[0] if matched_admin else "NOT FOUND")

        # 3. Verify availability in Donor Portal API
        print("\n--- 3. FETCHING FROM DONOR PORTAL API ---")
        donor_res = client.get("/api/donor/emergency-requests")
        donor_data = donor_res.get_json()
        print("Donor Active Count:", donor_data["count"])
        matched_donor = [r for r in donor_data["data"] if r["request_code"] == req_code]
        print("Donor Found Request:", matched_donor[0] if matched_donor else "NOT FOUND")

        # 4. Donor responds to Emergency Request
        print("\n--- 4. DONOR RESPONDS 'I CAN DONATE' ---")
        donor_resp_payload = {
            "donor_name": "Vikram Singh",
            "donor_phone": "9876543210",
            "donor_blood_group": "B+",
            "notes": "Available to donate at Lilavati Hospital tomorrow morning."
        }
        resp_res = client.post(f"/api/emergency-requests/{req_code}/respond", json=donor_resp_payload)
        print("Donor Response Result:", resp_res.get_json())

        # 5. Check Admin Details Modal endpoint for donor response
        print("\n--- 5. ADMIN VERIFIES DONOR PLEDGES ---")
        details_res = client.get(f"/api/emergency-requests/{req_code}")
        details_data = details_res.get_json()["data"]
        print("Request Details:", details_data["request_code"], "| Patient:", details_data["patient_name"])
        print("Pledged Donor Responses:", details_data["donor_responses"])
