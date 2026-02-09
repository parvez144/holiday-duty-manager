from extensions import db

class IClockTransaction(db.Model):
    __bind_key__ = 'bio_time'
    __tablename__ = 'iclock_transaction'

    id = db.Column(db.Integer, primary_key=True)
    emp_code = db.Column(db.String(20), nullable=False)
    punch_time = db.Column(db.DateTime, nullable=False)
    
    # Other columns exist but we only need these for now.

    def __repr__(self):
        return f'<Punch {self.emp_code} @ {self.punch_time}>'
