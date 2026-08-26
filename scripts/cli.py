import sys
import argparse
from app.main import create_app
from app.config import Config
from app.database.connection import db
from app.database.models.user import User, UserSession, UserAuditLog
from app.database.models.donor import DonorProfile
from app.database.seed import seed_all
from app.users.models import UserRole, UserStatus
from app.security.password_policy import PasswordPolicyEngine

def main():
    parser = argparse.ArgumentParser(description="RaktDaan Enterprise Management CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available Commands")

    # Command: status
    subparsers.add_parser("status", help="Displays system health and database statistics")

    # Command: seed
    subparsers.add_parser("seed", help="Runs database initialization and seed pipeline")

    # Command: create-admin
    admin_parser = subparsers.add_parser("create-admin", help="Creates a new system administrator")
    admin_parser.add_argument("--name", required=True, help="Admin Full Name")
    admin_parser.add_argument("--email", required=True, help="Admin Email")
    admin_parser.add_argument("--password", required=True, help="Admin Password")
    admin_parser.add_argument("--phone", default="9876543210", help="Admin Phone")

    # Command: list-users
    subparsers.add_parser("list-users", help="Lists all registered users in the database")

    args = parser.parse_args()

    app = create_app()
    with app.app_context():
        if args.command == "status":
            user_count = User.query.count()
            donor_count = DonorProfile.query.count()
            audit_count = UserAuditLog.query.count()
            print("==========================================")
            print(f" App Name:      {Config.PROJECT_NAME}")
            print(f" Version:       {Config.VERSION}")
            print(f" Total Users:   {user_count}")
            print(f" Total Donors:  {donor_count}")
            print(f" Audit Logs:    {audit_count}")
            print("==========================================")

        elif args.command == "seed":
            seed_all()
            print("Database seeding completed successfully.")

        elif args.command == "create-admin":
            email = args.email.lower().strip()
            existing = User.query.filter_by(email=email).first()
            if existing:
                print(f"Error: User with email '{email}' already exists.")
                sys.exit(1)

            admin = User(
                name=args.name,
                email=email,
                password_hash=PasswordPolicyEngine.hash_password(args.password),
                role=UserRole.ADMIN.value,
                phone=args.phone,
                status=UserStatus.ACTIVE.value
            )
            db.session.add(admin)
            db.session.commit()
            print(f"Admin '{email}' created successfully.")

        elif args.command == "list-users":
            users = User.query.all()
            print(f"{'ID':<5} {'Name':<20} {'Email':<30} {'Role':<10} {'Status':<10}")
            print("-" * 75)
            for u in users:
                print(f"{u.id:<5} {u.name:<20} {u.email:<30} {u.role:<10} {u.status:<10}")

        else:
            parser.print_help()

if __name__ == "__main__":
    main()
