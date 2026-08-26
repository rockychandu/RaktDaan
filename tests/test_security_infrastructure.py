from app.security.password_policy import PasswordPolicyEngine
from app.security.field_encryption import FieldEncryptor
from app.security.sanitizer import InputSanitizer
from app.security.rbac_matrix import RBACPermissionMatrix, Permission

def test_password_entropy_calculation():
    weak_entropy = PasswordPolicyEngine.evaluate_entropy("password")
    strong_entropy = PasswordPolicyEngine.evaluate_entropy("P@ssw0rd123!Secure")
    assert strong_entropy > weak_entropy

def test_pii_field_encryption_decryption():
    plain_address = "123 Healthcare Boulevard, Suite 400"
    encrypted = FieldEncryptor.encrypt(plain_address)
    assert encrypted != plain_address
    assert encrypted.startswith("ENC:")
    decrypted = FieldEncryptor.decrypt(encrypted)
    assert decrypted == plain_address

def test_input_sanitizer_xss_protection():
    raw_html = "<script>alert('xss');</script>"
    clean = InputSanitizer.sanitize_string(raw_html)
    assert "<script>" not in clean
    assert "&lt;script&gt;" in clean

def test_rbac_permission_matrix():
    assert RBACPermissionMatrix.has_permission("ADMIN", Permission.MANAGE_ADMINS) is True
    assert RBACPermissionMatrix.has_permission("DONOR", Permission.MANAGE_ADMINS) is False
    assert RBACPermissionMatrix.has_permission("DONOR", Permission.READ_OWN_PROFILE) is True
