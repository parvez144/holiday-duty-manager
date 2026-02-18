from extensions import db
from datetime import datetime

class NightBillRate(db.Model):
    __tablename__ = 'night_bill_rates'
    
    id = db.Column(db.Integer, primary_key=True)
    designation = db.Column(db.String(100), unique=True, nullable=False)
    rate = db.Column(db.Float, nullable=False, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def __init__(self, designation, rate):
        self.designation = designation
        self.rate = rate

    def __repr__(self):
        return f'<NightBillRate {self.designation}: {self.rate}>'
