from datetime import datetime
from extensions import db

class ManualBill(db.Model):
    __tablename__ = 'manual_bills'
    
    id = db.Column(db.Integer, primary_key=True)
    bill_date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    title = db.Column(db.String(255), nullable=False)
    prepared_by = db.Column(db.String(255), nullable=True)
    total_amount = db.Column(db.Numeric(15, 2), default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    items = db.relationship('ManualBillItem', backref='bill', cascade="all, delete-orphan", lazy=True)
    
    def __repr__(self):
        return f'<ManualBill {self.title} - {self.bill_date}>'


class ManualBillItem(db.Model):
    __tablename__ = 'manual_bill_items'
    
    id = db.Column(db.Integer, primary_key=True)
    bill_id = db.Column(db.Integer, db.ForeignKey('manual_bills.id'), nullable=False)
    
    emp_id = db.Column(db.String(50), nullable=True)
    name = db.Column(db.String(255), nullable=False)
    designation = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)
    
    qty = db.Column(db.Numeric(10, 2), default=1)
    rate = db.Column(db.Numeric(15, 2), default=0)
    amount = db.Column(db.Numeric(15, 2), default=0)
    
    def __repr__(self):
        return f'<ManualBillItem {self.name} - {self.amount}>'
