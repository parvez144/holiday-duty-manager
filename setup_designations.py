import csv
import os
from app import app
from extensions import db
from models.designation import Designation

def setup_designations():
    csv_path = 'designation.csv'
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found.")
        return

    with app.app_context():
        # 1. Create the table if it doesn't exist
        print("Ensuring Designations table exists...")
        db.create_all()

        # 2. Read CSV and populate
        print(f"Reading designations from {csv_path}...")
        
        try:
            with open(csv_path, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                count_added = 0
                count_updated = 0
                
                for row in reader:
                    designation_name = row.get('Designation', '').strip()
                    if not designation_name:
                        continue
                        
                    # Parse numerical fields
                    def to_float(val):
                        try:
                            return float(val or 0)
                        except ValueError:
                            return 0.0

                    grade = row.get('Grade', '').strip()
                    att_bonus = to_float(row.get('Attendance_Bonus'))
                    night_bill = to_float(row.get('Night_Bill'))
                    holiday_bill = to_float(row.get('Holiday_Bill'))
                    lunch_bill = to_float(row.get('Lunch_Bill'))
                    tiffin_bill = to_float(row.get('Tiffin_Bill'))
                    actual_ot = row.get('Actual_OT', 'N').strip()
                    compliance_ot = row.get('Compliance_OT', 'N').strip()

                    existing = Designation.query.filter_by(designation=designation_name).first()
                    if not existing:
                        new_desig = Designation(
                            designation=designation_name,
                            grade=grade,
                            attendance_bonus=att_bonus,
                            night_bill=night_bill,
                            holiday_bill=holiday_bill,
                            lunch_bill=lunch_bill,
                            tiffin_bill=tiffin_bill,
                            actual_ot=actual_ot,
                            compliance_ot=compliance_ot
                        )
                        db.session.add(new_desig)
                        count_added += 1
                        print(f"Added designation: {designation_name}")
                    else:
                        # Update existing fields
                        existing.grade = grade
                        existing.attendance_bonus = att_bonus
                        existing.night_bill = night_bill
                        existing.holiday_bill = holiday_bill
                        existing.lunch_bill = lunch_bill
                        existing.tiffin_bill = tiffin_bill
                        existing.actual_ot = actual_ot
                        existing.compliance_ot = compliance_ot
                        count_updated += 1
                
                db.session.commit()
                print(f"Designation setup complete! Added: {count_added}, Updated: {count_updated}")
                
        except Exception as e:
            print(f"An error occurred: {e}")
            db.session.rollback()

if __name__ == "__main__":
    setup_designations()
