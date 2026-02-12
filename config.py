import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

# Database Settings
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT', '3306')
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')

# Flask Security Key
SECRET_KEY = os.getenv('SECRET_KEY')

# Main Database (MFL)
SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/mfl"

# Secondary Database (BioTime)
SQLALCHEMY_BINDS = {
    'bio_time': f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/bio_time"
}

SQLALCHEMY_TRACK_MODIFICATIONS = False

