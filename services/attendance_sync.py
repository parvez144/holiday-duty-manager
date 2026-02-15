from models.attendance import IClockTransaction
from extensions import db
from sqlalchemy import func
import logging

# Define Remote Model locally to isolate BioTime dependency
class BioTimeTransaction(db.Model):
    __bind_key__ = 'bio_time'
    __tablename__ = 'iclock_transaction'

    id = db.Column(db.Integer, primary_key=True)
    emp_code = db.Column(db.String(20), nullable=False)
    punch_time = db.Column(db.DateTime, nullable=False)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def sync_attendance():
    """
    Synchronizes punch data from BioTimeTransaction (remote) 
    to IClockTransaction (local).
    """
    try:
        # 1. Get the latest sync_id from local table
        latest_sync = db.session.query(func.max(IClockTransaction.sync_id)).scalar()
        if latest_sync is None:
            latest_sync = 0
        
        logger.info(f"Starting sync from sync_id: {latest_sync}")

        # 2. Fetch new records from remote table
        # We only sync 'id', 'emp_code', and 'punch_time'
        new_records = BioTimeTransaction.query.filter(BioTimeTransaction.id > latest_sync).order_by(BioTimeTransaction.id).all()

        if not new_records:
            logger.info("No new records to sync.")
            return 0

        # 3. Bulk insert into local table
        sync_count = 0
        for record in new_records:
            # Check if this sync_id already exists (sanity check)
            existing = IClockTransaction.query.filter_by(sync_id=record.id).first()
            if not existing:
                local_record = IClockTransaction(
                    emp_code=record.emp_code,
                    punch_time=record.punch_time,
                    sync_id=record.id,
                    original_punch_time=record.punch_time
                )
                db.session.add(local_record)
                sync_count += 1
            
            # Flush every 100 records to keep memory usage low
            if sync_count % 100 == 0:
                db.session.flush()

        db.session.commit()
        logger.info(f"Successfully synced {sync_count} new records.")
        return sync_count

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error during attendance sync: {str(e)}")
        raise e
