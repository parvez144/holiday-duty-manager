import os
from dotenv import load_dotenv
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

# Main Database (MFL)
SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{quote_plus(DB_USER)}:{quote_plus(DB_PASS)}@{DB_HOST}:{DB_PORT}/mfl"

# Secondary Database (BioTime)
SQLALCHEMY_BINDS = {
    'bio_time': f"mysql+pymysql://{quote_plus(DB_USER)}:{quote_plus(DB_PASS)}@{DB_HOST}:{DB_PORT}/bio_time"
}

SQLALCHEMY_TRACK_MODIFICATIONS = False

