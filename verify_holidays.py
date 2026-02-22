from app import app
from models.holiday import Holiday
from extensions import db

with app.app_context():
    holidays = Holiday.query.all()
    for h in holidays:
        print(f"ID: {h.id}, Name: {h.holiday_name}, Date: {h.holiday_date}, Status: {h.status}, Processed: {h.processed_at}")
