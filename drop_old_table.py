from app import app
from extensions import db
from sqlalchemy import text

with app.app_context():
    print("Dropping night_bill_rates table...")
    try:
        db.session.execute(text("DROP TABLE IF EXISTS night_bill_rates"))
        db.session.commit()
        print("Table dropped successfully!")
    except Exception as e:
        print(f"Error: {e}")
        db.session.rollback()
