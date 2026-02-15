import os
from dotenv import load_dotenv
from datetime import timedelta
from urllib.parse import quote_plus

# Load variables from .env file
load_dotenv()

# Database Settings
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT', '3306')
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')

db_config = {
    'host': DB_HOST,
    'port': DB_PORT,
    'user': DB_USER,
    'password': DB_PASS,
    'database': 'mfl'
}

# Flask Security Key
SECRET_KEY = os.getenv('SECRET_KEY')

# Remote Database Settings
REMOTE_DB_HOST = os.getenv('REMOTE_DB_HOST') or DB_HOST
REMOTE_DB_PORT = os.getenv('REMOTE_DB_PORT') or '3306'
REMOTE_DB_USER = os.getenv('REMOTE_DB_USER') or DB_USER
REMOTE_DB_PASS = os.getenv('REMOTE_DB_PASS') or DB_PASS
REMOTE_DB_NAME = os.getenv('REMOTE_DB_NAME') or 'bio_time'

# Main Database (MFL)
SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{quote_plus(DB_USER)}:{quote_plus(DB_PASS)}@{DB_HOST}:{DB_PORT}/mfl"

# Secondary Database (BioTime - Remote)
SQLALCHEMY_BINDS = {
    'bio_time': f"mysql+pymysql://{quote_plus(REMOTE_DB_USER)}:{quote_plus(REMOTE_DB_PASS)}@{REMOTE_DB_HOST}:{REMOTE_DB_PORT}/{REMOTE_DB_NAME}"
}

SQLALCHEMY_TRACK_MODIFICATIONS = False

# Session Lifetime
PERMANENT_SESSION_LIFETIME = timedelta(minutes=int(os.getenv('SESSION_TIMEOUT_MINUTES') or 30))

