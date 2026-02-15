from flask import Blueprint, render_template
from flask_login import login_required

night_bill_bp = Blueprint('night_bill', __name__)

@night_bill_bp.route('/night_bill')
@login_required
def night_bill_page():
    return render_template('night_bill.html')
