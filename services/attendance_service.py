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
    query = db.session.query(
        IClockTransaction.emp_code,
        func.min(IClockTransaction.punch_time).label('in_time'),
        func.max(IClockTransaction.punch_time).label('out_time')
    ).filter(func.date(IClockTransaction.punch_time) == report_date)

    if emp_ids:
        query = query.filter(IClockTransaction.emp_code.in_(emp_ids))
    
    query = query.group_by(IClockTransaction.emp_code)
    
    results = query.all()

    attendance_data = {}
    for row in results:
        attendance_data[str(row.emp_code)] = {
            'in_time': row.in_time,
            'out_time': row.out_time
        }
    
    return attendance_data

if __name__ == "__main__":
    # To run this standalone, we need to setup the app context
    from app import app
    with app.app_context():
        data = get_attendance_for_date("2021-10-02")
        print(f"Total records found: {len(data)}")
