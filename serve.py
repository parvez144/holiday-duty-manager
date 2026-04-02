import os
# Suppress GLib-GIO warnings on Windows
os.environ['GIO_USE_VFS'] = 'local'
os.environ['G_MESSAGES_DEBUG'] = 'none'

from waitress import serve
from app import app
import logging


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger('waitress')
    
    port = 5100
    host = '127.0.0.1'
    
    print(f"Starting Holiday Duty Manager on http://{host}:{port}")
    print("Press Ctrl+C to stop.")
    
    # Run the app with Waitress
    serve(app, host=host, port=port, threads=6)
