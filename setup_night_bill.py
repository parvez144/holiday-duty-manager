from app import app
from extensions import db
from models.night_bill_rate import NightBillRate

with app.app_context():
    # 1. Create the table
    print("Creating Night Bill Rate table...")
    db.create_all()
    print("Table created successfully!")

    # 2. Seed some designations
    sample_rates = [
        ('Manager', 500.0),
        ('Assistant Manager', 400.0),
        ('Sr. Executive', 300.0),
        ('Executive', 250.0),
        ('Sr. Officer', 200.0),
        ('Officer', 150.0),
        ('Jr. Officer', 100.0),
    ]

    print("Seeding initial rates...")
    for designation, rate in sample_rates:
        # Case insensitive match check if possible, though designation in DB is String(100)
        existing = NightBillRate.query.filter_by(designation=designation).first()
        if not existing:
            new_rate = NightBillRate(designation=designation, rate=rate)
            db.session.add(new_rate)
            print(f"Added rate for {designation}: {rate}")
        else:
            existing.rate = rate # Update if exists
            print(f"Updated rate for {designation}: {rate}")

    db.session.commit()
    print("Seeding complete!")
