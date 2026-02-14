import os
from datetime import datetime
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

# System & Developer Information
COMPANY_NAME = 'Manel Fashion Limited'
VERSION = '1.0.0'

system_info = {
    'version': VERSION,
    'developer': {
        'text': f'Built for {COMPANY_NAME} by',
        'name': 'Shahriar',
        'website': 'https://github.com/parvez144'
    },
    'copyright': {
        'start_year': 2026,
        'year': datetime.now().year,
        'holder': 'SPK',
        'text': 'All rights reserved.',
        'version': VERSION,
    },
    'company': {
        'name': COMPANY_NAME,
        'address': 'Bason 79/1, Vitipara, Gazipur Sadar, Gazipur.',
        'url': 'https://manelfashion.net',
        'logo': 'img/logo.png'
    }
}

user = {
    'username': 'spk',
    'role': 'Admin',
    'name': os.getenv('ADMIN_NAME'),
    'phone': os.getenv('ADMIN_PHONE'),
}

