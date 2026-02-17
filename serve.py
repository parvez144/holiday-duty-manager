from waitress import serve
from app import app
import logging
import os

if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger('waitress')
    
    port = 5100
    print(f"Starting Holiday Duty Manager on http://0.0.0.0:{port}")
    print("Press Ctrl+C to stop.")
    
    # Run the app with Waitress
    serve(app, host='0.0.0.0', port=port, threads=6)
