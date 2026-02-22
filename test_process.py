from app import app
from models.holiday import Holiday, HolidayDutyRecord
from services.report_service import process_holiday_duty
from extensions import db

with app.app_context():
    holiday_id = 3
    h = Holiday.query.get(holiday_id)
    if h:
        print(f"Before: {h.holiday_name}, Status: {h.status}")
        h.status = 'draft'
        db.session.commit()
        
        print("Processing holiday...")
        count = process_holiday_duty(holiday_id)
        print(f"Processed {count} records.")
        
        # Verify security records
        sec_records = HolidayDutyRecord.query.filter(
            (HolidayDutyRecord.holiday_id == holiday_id) & 
            ((HolidayDutyRecord.sub_section == 'Security') | (HolidayDutyRecord.section == 'Security'))
        ).all()
        
        print(f"Found {len(sec_records)} security records in snapshot.")
        for r in sec_records:
            print(f"ID: {r.emp_id}, Name: {r.emp_name}, Amount: {r.amount}")
            
        h.status = 'finalized'
        db.session.commit()
        print(f"After: Status reset to {h.status}")
    else:
        print("Holiday ID 3 not found")
