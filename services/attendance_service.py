from models.attendance import IClockTransaction
from extensions import db
from sqlalchemy import func
from datetime import datetime

def get_attendance_for_date(report_date, emp_ids=None):
    """
    Fetches attendance records (In/Out times) for given employees on a specific date.
    
    :param report_date: string (YYYY-MM-DD) or date object
    :param emp_ids: List of employee IDs (optional). If None, fetches for all.
    :return: Dictionary {emp_code: {'in_time': datetime, 'out_time': datetime}}
    """
    # In-Time: Earliest punch before 1:00 PM (13:00)
    # Out-Time: Latest punch at or after 1:00 PM (13:00)
    
    query = db.session.query(
        IClockTransaction.emp_code,
        IClockTransaction.punch_time
    ).filter(func.date(IClockTransaction.punch_time) == report_date)

    if emp_ids:
        query = query.filter(IClockTransaction.emp_code.in_(emp_ids))
    
    results = query.all()

    attendance_data = {}
    
    # Process results to find min before 1 PM and max at/after 1 PM per employee
    for row in results:
        eid = str(row.emp_code).strip()
        punch = row.punch_time
        
        if eid not in attendance_data:
            attendance_data[eid] = {'morning_punches': [], 'afternoon_punches': []}
        
        if punch.hour < 13:
            attendance_data[eid]['morning_punches'].append(punch)
        else:
            attendance_data[eid]['afternoon_punches'].append(punch)

    final_data = {}
    for eid, data in attendance_data.items():
        # User Rule: In-Time must be before 1 PM
        in_time = min(data['morning_punches']) if data['morning_punches'] else None
        
        # User Rule: After 1 PM only Out-Time.
        # Out-Time MUST be at or after 1 PM.
        out_time = max(data['afternoon_punches']) if data['afternoon_punches'] else None

        final_data[eid] = {
            'in_time': in_time,
            'out_time': out_time
        }
    
    return final_data

def add_manual_punch(emp_code, punch_time):
    """
    Adds or updates a manual punch record.
    If a manual punch (is_corrected=True) already exists for the same employee,
    date, and session (Morning < 1PM, Afternoon >= 1PM), it updates it.
    """
    report_date = punch_time.date()
    is_morning = punch_time.hour < 13

    # Check for existing manual punch in the same session
    existing_query = IClockTransaction.query.filter(
        IClockTransaction.emp_code == emp_code,
        func.date(IClockTransaction.punch_time) == report_date,
        IClockTransaction.is_corrected == True
    )

    if is_morning:
        existing_query = existing_query.filter(func.hour(IClockTransaction.punch_time) < 13)
    else:
        existing_query = existing_query.filter(func.hour(IClockTransaction.punch_time) >= 13)

    existing_punch = existing_query.first()

    if existing_punch:
        # Update existing record
        existing_punch.punch_time = punch_time
        existing_punch.updated_at = datetime.now()
        db.session.commit()
        return existing_punch, "updated"
    else:
        # Create new record
        new_punch = IClockTransaction(
            emp_code=emp_code,
            punch_time=punch_time,
            is_corrected=True
        )
        db.session.add(new_punch)
        db.session.commit()
        return new_punch, "created"

if __name__ == "__main__":
    # To run this standalone, we need to setup the app context
    from app import app
    with app.app_context():
        data = get_attendance_for_date("2021-10-02")
        print(f"Total records found: {len(data)}")
