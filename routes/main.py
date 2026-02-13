from flask import Blueprint, render_template
from flask_login import login_required
from services.employee_service import get_employee_count, get_section_count
from datetime import datetime

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@login_required
def index():
    stats = {
        'employee_count': get_employee_count(),
        'section_count': get_section_count()
    }
    return render_template('dashboard.html', stats=stats, datetime=datetime)
