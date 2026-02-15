import sys
import os
from app import app
from extensions import db
from services.attendance_sync import sync_attendance
import time

def init_db():
    """Create the local tables if they don't exist."""
    print("Initializing local database tables...")
    with app.app_context():
        # This will only create tables for models that use the default bind (mfl)
        # and don't exist yet.
        db.create_all() 
    print("Database initialization complete.")

def run_sync():
    """Run the synchronization loop or once."""
    print("Starting synchronization...")
    with app.app_context():
        count = sync_attendance()
        print(f"Sync complete. {count} records added.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--init":
        init_db()
    
    # Run sync on start
    run_sync()

    # If --loop argument is passed, keep syncing every 60 minutes
    if "--loop" in sys.argv:
        print("Loop mode enabled. Syncing every 60 minutes (3600 seconds). Press Ctrl+C to stop.")
        try:
            while True:
                time.sleep(3600)
                run_sync()
        except KeyboardInterrupt:
            print("\nSync stopped.")
