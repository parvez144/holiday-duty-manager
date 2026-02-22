from app import app
from models.holiday import Holiday
from services.report_service import get_holiday_records
from datetime import datetime
from flask import render_template

with app.app_context():
    # Mocking the route logic for 2026-02-21
    start_date = '2026-02-21'
    end_date = '2026-02-21'
    
    target_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    holiday = Holiday.query.filter_by(holiday_date=target_date).first()
    
    if holiday and holiday.processed_at:
        print(f"Holiday found: {holiday.holiday_name}")
        rows = get_holiday_records(holiday.id, sub_section='Security')
        is_holiday_mode = True
        holiday_name = holiday.holiday_name
        
        print(f"Rows found: {len(rows)}")
        for r in rows:
            print(f" - {r['name']}: {r['amount']}")
            
        # Try to render (simulated)
        # Note: render_template needs a request context or just test the logic
        print(f"is_holiday_mode: {is_holiday_mode}")
        print(f"holiday_name: {holiday_name}")
    else:
        print("Holiday not found or not processed")
