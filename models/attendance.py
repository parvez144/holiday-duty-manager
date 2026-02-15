from extensions import db
from datetime import datetime

class IClockTransaction(db.Model):
    """Local table in 'mfl' database for corrections and sync data."""
    __tablename__ = 'iclock_transaction'

    id = db.Column(db.Integer, primary_key=True)
    emp_code = db.Column(db.String(20), nullable=False, index=True)
    punch_time = db.Column(db.DateTime, nullable=False, index=True)
    
    # Sync metadata
    sync_id = db.Column(db.Integer, unique=True, nullable=True) # Original ID from BioTime
    is_corrected = db.Column(db.Boolean, default=False)
    original_punch_time = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<LocalPunch {self.emp_code} @ {self.punch_time}>'
