from extensions import db
from datetime import datetime

class Designation(db.Model):
    __tablename__ = 'designations'
    
    id = db.Column(db.Integer, primary_key=True)
    designation = db.Column(db.String(150), unique=True, nullable=False)
    grade = db.Column(db.String(100))
    attendance_bonus = db.Column(db.Float, default=0.0)
    night_bill = db.Column(db.Float, default=0.0)
    holiday_bill = db.Column(db.Float, default=0.0)
    lunch_bill = db.Column(db.Float, default=0.0)
    tiffin_bill = db.Column(db.Float, default=0.0)
    actual_ot = db.Column(db.String(10), default='N')
    compliance_ot = db.Column(db.String(10), default='N')
    
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f'<Designation {self.designation}>'
