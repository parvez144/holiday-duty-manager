import sys
from app import app
from extensions import db
from models.user import User

def create_user(username, password, name, role='User'):
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
        print(f"User '{username}' ({role}) created successfully!")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python create_user.py <username> <password> <name> [role]")
        print("Example: python create_user.py parvez secret123 'Shahriar Parvez' Admin")
        sys.exit(1)
    
    username = sys.argv[1]
    password = sys.argv[2]
    name = sys.argv[3]
    role = sys.argv[4] if len(sys.argv) > 4 else 'User'
    
    create_user(username, password, name, role)
