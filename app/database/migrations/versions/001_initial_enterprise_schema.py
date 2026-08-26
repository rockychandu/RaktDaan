"""
Initial Enterprise Schema Migration for RaktDaan Blood Bank System
Revision ID: 001_initial_enterprise_schema
Revises: None
Create Date: 2026-08-26 11:46:30.000000
"""

from alembic import op
import sqlalchemy as sa

revision = '001_initial_enterprise_schema'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # --- 1. Users Table ---
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=150), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=20), server_default='DONOR', nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=False),
        sa.Column('status', sa.String(length=20), server_default='ACTIVE', nullable=False),
        sa.Column('failed_login_attempts', sa.Integer(), server_default='0', nullable=False),
        sa.Column('locked_until', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), server_default='0', nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_users_email', 'users', ['email'], unique=True)
    op.create_index('idx_users_role', 'users', ['role'], unique=False)
    op.create_index('idx_users_status', 'users', ['status'], unique=False)
    op.create_index('idx_users_is_deleted', 'users', ['is_deleted'], unique=False)

    # --- 2. Donor Profiles Table ---
    op.create_table(
        'donor_profiles',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('date_of_birth', sa.Date(), nullable=False),
        sa.Column('gender', sa.String(length=20), nullable=False),
        sa.Column('blood_group', sa.String(length=10), nullable=False),
        sa.Column('address_encrypted', sa.String(length=255), nullable=False),
        sa.Column('city', sa.String(length=100), nullable=False),
        sa.Column('state', sa.String(length=100), nullable=False),
        sa.Column('emergency_contact_encrypted', sa.String(length=255), nullable=False),
        sa.Column('eligibility_status', sa.String(length=30), server_default='ELIGIBLE', nullable=False),
        sa.Column('last_donation_date', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), server_default='0', nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index('idx_donor_blood_group', 'donor_profiles', ['blood_group'], unique=False)
    op.create_index('idx_donor_city', 'donor_profiles', ['city'], unique=False)
    op.create_index('idx_donor_state', 'donor_profiles', ['state'], unique=False)
    op.create_index('idx_donor_eligibility', 'donor_profiles', ['eligibility_status'], unique=False)

    # --- 3. User Sessions Table ---
    op.create_table(
        'user_sessions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('session_token_jti', sa.String(length=255), nullable=False),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=255), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='1', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), server_default='0', nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_sessions_jti', 'user_sessions', ['session_token_jti'], unique=True)
    op.create_index('idx_sessions_user', 'user_sessions', ['user_id'], unique=False)

    # --- 4. User Audit Logs Table ---
    op.create_table(
        'user_audit_logs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('action_type', sa.String(length=50), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=False),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('metadata_json', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), server_default='0', nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_audit_action', 'user_audit_logs', ['action_type'], unique=False)
    op.create_index('idx_audit_user', 'user_audit_logs', ['user_id'], unique=False)

    # --- 5. Blood Inventory Table ---
    op.create_table(
        'blood_inventory',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('blood_group', sa.String(length=10), nullable=False),
        sa.Column('units_available', sa.Integer(), server_default='0', nullable=False),
        sa.Column('units_reserved', sa.Integer(), server_default='0', nullable=False),
        sa.Column('units_expired', sa.Integer(), server_default='0', nullable=False),
        sa.Column('last_updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), server_default='0', nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_inventory_bg', 'blood_inventory', ['blood_group'], unique=True)


def downgrade():
    op.drop_table('blood_inventory')
    op.drop_table('user_audit_logs')
    op.drop_table('user_sessions')
    op.drop_table('donor_profiles')
    op.drop_table('users')
