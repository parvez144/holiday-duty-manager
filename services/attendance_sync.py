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

from sqlalchemy.dialects.mysql import insert as mysql_insert

def sync_attendance(batch_size=1000):
    """
    Synchronizes punch data from BioTimeTransaction (remote) 
    to IClockTransaction (local).
    Uses MySQL INSERT IGNORE for robustness against duplicates.
    """
    try:
        # Clear session to avoid stale data
        db.session.expire_all()
        
        # 1. Get the latest sync_id from local table
        latest_sync = db.session.query(func.max(IClockTransaction.sync_id)).scalar() or 0
        
        logger.info(f"Checking for new records starting from sync_id: {latest_sync}...")

        # 2. Sync in batches
        total_synced = 0
        while True:
            # Fetch a batch of records from remote
            new_records = BioTimeTransaction.query.filter(
                BioTimeTransaction.id > latest_sync
            ).order_by(BioTimeTransaction.id).limit(batch_size).all()

            if not new_records:
                break

            # Use MySQL-specific INSERT IGNORE via prefix_with if using standard insert
            # Or use on_duplicate_key_update
            
            mappings = []
            for record in new_records:
                mappings.append({
                    'emp_code': record.emp_code,
                    'punch_time': record.punch_time,
                    'sync_id': record.id,
                    'original_punch_time': record.punch_time
                })
                latest_sync = record.id

            # Execute bulk insert with ignore
            stmt = mysql_insert(IClockTransaction).values(mappings)
            # This will skip duplicates based on sync_id (unique constraint)
            stmt = stmt.on_duplicate_key_update(sync_id=IClockTransaction.sync_id) 
            
            db.session.execute(stmt)
            db.session.commit()
            
            total_synced += len(new_records)
            logger.info(f"Processed {total_synced} records (Latest Sync ID: {latest_sync})")

        if total_synced == 0:
            logger.info("No new records to sync.")
        else:
            logger.info(f"Sync complete. Total processed: {total_synced}")
            
        return total_synced

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error during attendance sync: {str(e)}")
        raise e
