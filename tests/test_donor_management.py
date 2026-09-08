"""
Unit & Integration Tests for Donor Management System (Member 3).
"""

import pytest
from app.services.donor_service import DonorService
from app.common.exceptions import DuplicateDonorException, DonorNotFoundException


def test_register_donor_success(app):
    with app.app_context():
        payload = {
            "name": "Test Donor One",
            "email": "testdonor1@example.com",
            "password": "Password@123",
            "phone": "9876543211",
            "date_of_birth": "1995-05-15",
            "gender": "Male",
            "blood_group": "O+",
            "address": "123 Main Street",
            "city": "Mumbai",
            "state": "Maharashtra",
            "emergency_contact": "9876543212"
        }
        user, donor = DonorService.register_donor(payload)
        assert user.id is not None
        assert donor.id is not None
        assert donor.blood_group == "O+"
        assert donor.city == "Mumbai"


def test_register_donor_duplicate_email(app):
    with app.app_context():
        payload1 = {
            "name": "Test Donor Base",
            "email": "dup@example.com",
            "password": "Password@123",
            "phone": "9876543290",
            "date_of_birth": "1992-08-20",
            "gender": "Female",
            "blood_group": "A+",
            "address": "456 Side Street",
            "city": "Delhi",
            "state": "Delhi",
            "emergency_contact": "9876543291"
        }
        DonorService.register_donor(payload1)

        payload2 = {
            "name": "Test Donor Dup",
            "email": "dup@example.com", # Duplicate Email
            "password": "Password@123",
            "phone": "9876543299",
            "date_of_birth": "1992-08-20",
            "gender": "Female",
            "blood_group": "A+",
            "address": "456 Side Street",
            "city": "Delhi",
            "state": "Delhi",
            "emergency_contact": "9876543298"
        }
        with pytest.raises(DuplicateDonorException):
            DonorService.register_donor(payload2)


def test_update_and_soft_delete_donor(app):
    with app.app_context():
        payload = {
            "name": "Test Donor Three",
            "email": "testdonor3@example.com",
            "password": "Password@123",
            "phone": "9876543300",
            "date_of_birth": "1990-01-10",
            "gender": "Male",
            "blood_group": "B+",
            "address": "789 Park Road",
            "city": "Pune",
            "state": "Maharashtra",
            "emergency_contact": "9876543301"
        }
        user, donor = DonorService.register_donor(payload)

        # Update Profile
        updated = DonorService.update_donor_profile(donor.id, {"city": "Nagpur"})
        assert updated.city == "Nagpur"

        # Soft Delete
        res = DonorService.soft_delete_donor(donor.id)
        assert res is True

        # Verify NotFound when querying active
        with pytest.raises(DonorNotFoundException):
            DonorService.get_donor_by_id(donor.id)

        # Restore
        restored = DonorService.restore_donor(donor.id)
        assert restored.is_deleted is False
