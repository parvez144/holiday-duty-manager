from app import app
from extensions import db
from models.attendance import IClockTransaction
from sqlalchemy import func

with app.app_context():
    max_sync_id = db.session.query(func.max(IClockTransaction.sync_id)).scalar()
    count = db.session.query(IClockTransaction).count()
    
    print(f"Max Sync ID reported: {max_sync_id}")
    print(f"Total Count: {count}")
    
    # Check if a specific ID exists
    target_id = 209129
    exists = db.session.query(IClockTransaction).filter_by(sync_id=target_id).first()
    if exists:
        print(f"Found record with sync_id {target_id}: {exists}")
    else:
        print(f"Record with sync_id {target_id} NOT found.")

    # Find IDs higher than reported max
    if max_sync_id:
        higher_records = db.session.query(IClockTransaction).filter(IClockTransaction.sync_id > max_sync_id).all()
        if higher_records:
            print(f"Found {len(higher_records)} records with sync_id GREATER than {max_sync_id}!")
            for r in higher_records[:5]:
                print(r)
        else:
            print(f"No records found with sync_id higher than {max_sync_id}.")
