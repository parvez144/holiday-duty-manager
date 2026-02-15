import argparse
from app import app
from extensions import db
from models.user import User
from dotenv import load_dotenv

load_dotenv()

def init_db():
    """Initialize database and create default admin user."""
    with app.app_context():
        print("Initializing database...")
        db.create_all()
        
        username = os.getenv('ADMIN_USERNAME', 'admin')
        password = os.getenv('ADMIN_PASSWORD', 'admin123')
        
        if User.query.filter_by(username=username).first():
            print(f"Notice: Admin user '{username}' already exists.")
        else:
            admin = User(
                username=username,
                name=os.getenv('ADMIN_NAME', 'Administrator'),
                role='Admin'
            )
            admin.set_password(password)
            db.session.add(admin)
            db.session.commit()
            print(f"Success: Admin user '{username}' created!")
        print("Done.")

def create_user(username, password, name, role='User'):
    """Create a new user with specified details."""
    with app.app_context():
        if User.query.filter_by(username=username).first():
            print(f"Error: User '{username}' already exists.")
            return

        new_user = User(
            username=username,
            name=name,
            role=role
        )
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        print(f"Success: User '{username}' ({role}) created successfully!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Holiday Duty Manager - User Management Tool")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Command: init
    subparsers.add_parser("init", help="Initialize database and create default admin")

    # Command: create-user
    create_parser = subparsers.add_parser("create-user", help="Create a new user")
    create_parser.add_argument("username", help="Username for the new account")
    create_parser.add_argument("password", help="Password for the new account")
    create_parser.add_argument("name", help="Full name of the user")
    create_parser.add_argument("--role", default="User", choices=["Admin", "User"], help="Role (default: User)")

    args = parser.parse_args()

    if args.command == "init":
        init_db()
    elif args.command == "create-user":
        create_user(args.username, args.password, args.name, args.role)
    else:
        parser.print_help()
