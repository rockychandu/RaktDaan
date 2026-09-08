"""
RaktDaan Enterprise Domain Exception Hierarchy.
Extends Member 1's base DomainException for specialized Member 3 & Member 4 domain errors.
"""

from app.users.exceptions import DomainException


class DonorNotFoundException(DomainException):
    def __init__(self, donor_id: str | int):
        super().__init__(
            message=f"Donor with ID '{donor_id}' was not found in the system.",
            status_code=404,
            errors={"donor_id": f"Donor '{donor_id}' does not exist or has been deleted."}
        )


class DuplicateDonorException(DomainException):
    def __init__(self, field_name: str, field_value: str):
        super().__init__(
            message=f"A donor with {field_name} '{field_value}' already exists.",
            status_code=409,
            errors={field_name: f"Value '{field_value}' is already registered to another donor account."}
        )


class EligibilityEvaluationException(DomainException):
    def __init__(self, reason: str, errors: dict = None):
        super().__init__(
            message=f"Donor eligibility evaluation failed: {reason}",
            status_code=422,
            errors=errors or {"eligibility": reason}
        )


class DonationNotFoundException(DomainException):
    def __init__(self, donation_id: str | int):
        super().__init__(
            message=f"Donation record '{donation_id}' was not found.",
            status_code=404,
            errors={"donation_id": f"Donation record '{donation_id}' does not exist."}
        )


class InvalidDonationWorkflowState(DomainException):
    def __init__(self, current_state: str, target_state: str, reason: str = ""):
        super().__init__(
            message=f"Invalid donation state transition from '{current_state}' to '{target_state}'. {reason}",
            status_code=400,
            errors={"state_transition": f"Cannot move donation from '{current_state}' to '{target_state}'."}
        )


class BloodBagNotFoundException(DomainException):
    def __init__(self, bag_id: str | int):
        super().__init__(
            message=f"Blood bag '{bag_id}' was not found in inventory.",
            status_code=404,
            errors={"bag_id": f"Blood bag '{bag_id}' does not exist."}
        )


class IncompatibleBloodGroupException(DomainException):
    def __init__(self, donor_group: str, recipient_group: str, reason: str = ""):
        super().__init__(
            message=f"Blood group '{donor_group}' is incompatible with recipient group '{recipient_group}'. {reason}",
            status_code=422,
            errors={"compatibility": f"Incompatible blood groups: Donor ({donor_group}) -> Recipient ({recipient_group})."}
        )


class InvalidBagStatusTransition(DomainException):
    def __init__(self, current_status: str, target_status: str):
        super().__init__(
            message=f"Illegal blood bag transition from '{current_status}' to '{target_status}'.",
            status_code=400,
            errors={"status": f"Blood bag in status '{current_status}' cannot be moved to '{target_status}'."}
        )


class ExpiredBagOperationException(DomainException):
    def __init__(self, bag_code: str, action: str):
        super().__init__(
            message=f"Cannot execute '{action}' on expired blood bag '{bag_code}'.",
            status_code=400,
            errors={"expired_bag": f"Bag '{bag_code}' has expired and must be discarded."}
        )


class QuarantinedBagOperationException(DomainException):
    def __init__(self, bag_code: str, action: str):
        super().__init__(
            message=f"Cannot execute '{action}' on quarantined blood bag '{bag_code}'.",
            status_code=400,
            errors={"quarantined_bag": f"Bag '{bag_code}' is currently in quarantine."}
        )


class InsufficientStockException(DomainException):
    def __init__(self, blood_group: str, requested_units: int, available_units: int):
        super().__init__(
            message=f"Insufficient inventory for blood group '{blood_group}'. Requested: {requested_units}, Available: {available_units}.",
            status_code=400,
            errors={"stock": f"Only {available_units} units of {blood_group} are available (requested {requested_units})."}
        )


class StorageCapacityExceededException(DomainException):
    def __init__(self, unit_name: str, max_capacity: int, current_occupied: int):
        super().__init__(
            message=f"Storage unit '{unit_name}' capacity exceeded (Capacity: {max_capacity}, Occupied: {current_occupied}).",
            status_code=400,
            errors={"storage_capacity": f"Unit '{unit_name}' has no available slots."}
        )


class StorageUnitNotFoundException(DomainException):
    def __init__(self, unit_id: str | int):
        super().__init__(
            message=f"Storage unit '{unit_id}' was not found.",
            status_code=404,
            errors={"unit_id": f"Storage unit '{unit_id}' does not exist."}
        )


class ReservationConflictException(DomainException):
    def __init__(self, reservation_id: str | int, reason: str):
        super().__init__(
            message=f"Reservation conflict for '{reservation_id}': {reason}",
            status_code=409,
            errors={"reservation": reason}
        )


class ReservationNotFoundException(DomainException):
    def __init__(self, reservation_id: str | int):
        super().__init__(
            message=f"Reservation '{reservation_id}' was not found.",
            status_code=404,
            errors={"reservation_id": f"Reservation '{reservation_id}' does not exist."}
        )


class DispatchNotFoundException(DomainException):
    def __init__(self, dispatch_id: str | int):
        super().__init__(
            message=f"Dispatch record '{dispatch_id}' was not found.",
            status_code=404,
            errors={"dispatch_id": f"Dispatch record '{dispatch_id}' does not exist."}
        )


class QuarantineNotFoundException(DomainException):
    def __init__(self, quarantine_id: str | int):
        super().__init__(
            message=f"Quarantine record '{quarantine_id}' was not found.",
            status_code=404,
            errors={"quarantine_id": f"Quarantine record '{quarantine_id}' does not exist."}
        )


class ReconciliationNotFoundException(DomainException):
    def __init__(self, reconciliation_id: str | int):
        super().__init__(
            message=f"Reconciliation record '{reconciliation_id}' was not found.",
            status_code=404,
            errors={"reconciliation_id": f"Reconciliation record '{reconciliation_id}' does not exist."}
        )


class InvalidBloodGroupException(DomainException):
    def __init__(self, blood_group: str):
        super().__init__(
            message=f"Invalid human blood group group '{blood_group}'. Must be one of A+, A-, B+, B-, AB+, AB-, O+, O-.",
            status_code=400,
            errors={"blood_group": f"'{blood_group}' is not a valid blood group designation."}
        )


class InvalidComponentTypeException(DomainException):
    def __init__(self, component_type: str):
        super().__init__(
            message=f"Invalid blood component type '{component_type}'.",
            status_code=400,
            errors={"component_type": f"'{component_type}' is not a supported blood component type."}
        )
