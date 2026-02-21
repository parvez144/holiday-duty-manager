from extensions import db
from datetime import datetime

class Holiday(db.Model):
    __tablename__ = 'holidays'

    id = db.Column(db.Integer, primary_key=True)
    holiday_date = db.Column(db.Date, unique=True, nullable=False, index=True)
    holiday_name = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), default='draft') # 'draft', 'finalized'
    processed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    records = db.relationship('HolidayDutyRecord', backref='holiday', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Holiday {self.holiday_name} @ {self.holiday_date}>'

class HolidayDutyRecord(db.Model):
    __tablename__ = 'holiday_duty_records'

    id = db.Column(db.Integer, primary_key=True)
    holiday_id = db.Column(db.Integer, db.ForeignKey('holidays.id'), nullable=False, index=True)
    
    # Snapshot data of employee
    emp_id = db.Column(db.String(20), nullable=False, index=True)
    emp_name = db.Column(db.String(255))
    designation = db.Column(db.String(255))
    section = db.Column(db.String(255))
    sub_section = db.Column(db.String(255))
    category = db.Column(db.String(50))
    
    # Snapshot salary data
    gross_salary = db.Column(db.Numeric(15, 2))
    basic_salary = db.Column(db.Numeric(15, 2))
    
    # Attendance snapshot
    in_time = db.Column(db.String(10)) # Store as HH:MM or "Missing"
    out_time = db.Column(db.String(10))
    work_hours = db.Column(db.Float, default=0.0)
    ot_hours = db.Column(db.Float, default=0.0)
    ot_rate = db.Column(db.Numeric(15, 2))
    
    # Financial result
    amount = db.Column(db.Numeric(15, 2), default=0.0)
    
    # Metadata
    is_manual = db.Column(db.Boolean, default=False)
    remarks = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f'<HolidayDutyRecord {self.emp_id} @ Holiday {self.holiday_id}>'
