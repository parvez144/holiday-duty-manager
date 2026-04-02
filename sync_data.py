import sys
import os
# Suppress GLib-GIO warnings on Windows (harmless but noisy)
os.environ['GIO_USE_VFS'] = 'local'
os.environ['G_MESSAGES_DEBUG'] = 'none'

import errno
import time
import signal
from app import app
from extensions import db
from services.attendance_sync import sync_attendance

def is_running(pid):
    """Check if a process with the given PID is still running."""
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True

def init_db():
    """Create the local tables if they don't exist."""
    print("Initializing local database tables...")
    
    # Create database if it doesn't exist
    import pymysql
    from config import DB_HOST, DB_PORT, DB_USER, DB_PASS
    
    try:
        connection = pymysql.connect(
            host=DB_HOST,
            port=int(DB_PORT),
            user=DB_USER,
            password=DB_PASS
        )
        with connection.cursor() as cursor:
            cursor.execute("CREATE DATABASE IF NOT EXISTS mfl")
        connection.close()
        print("Database 'mfl' checked/created.")
    except Exception as e:
        print(f"Warning: Could not check/create database 'mfl' automatically: {e}")

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
    # Robust lock mechanism using PID to handle stale locks
    lock_file = "sync.lock"
    
    if os.path.exists(lock_file):
        try:
            with open(lock_file, "r") as f:
                old_pid = int(f.read().strip())
            if is_running(old_pid):
                print(f"Error: Another synchronization process (PID {old_pid}) is already running.")
                sys.exit(1)
            else:
                print(f"Stale lock found (PID {old_pid} is dead). Overwriting...")
        except (ValueError, IOError):
            print("Corrupt lock file found. Overwriting...")

    try:
        # Create/overwrite the lock file with current PID
        with open(lock_file, "w") as f:
            f.write(str(os.getpid()))
    except Exception as e:
        print(f"Error creating lock file: {e}")
        sys.exit(1)

    try:
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
    finally:
        # Release the lock
        os.close(fd)
        try:
            os.remove(lock_file)
        except OSError:
            pass
