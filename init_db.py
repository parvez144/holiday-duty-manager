from app import app
from extensions import db
from models.user import User
import os
from dotenv import load_dotenv

load_dotenv()

def create_admin():
    with app.app_context():
        # Create tables
        db.create_all()
        
        username = os.getenv('ADMIN_USERNAME', 'admin')
        password = os.getenv('ADMIN_PASSWORD', 'admin123')
        
        if User.query.filter_by(username=username).first():
            print(f"User {username} already exists.")
            return

        admin = User(
            username=username,
            name=os.getenv('ADMIN_NAME', 'Administrator'),
            role='Admin'
        )
        admin.set_password(password)
        
        db.session.add(admin)
        db.session.commit()
        print(f"Admin user '{username}' created successfully!")

if __name__ == "__main__":
    create_admin()
