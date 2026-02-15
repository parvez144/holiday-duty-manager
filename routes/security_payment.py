from flask import Blueprint, render_template
from flask_login import login_required

security_payment_bp = Blueprint('security_payment', __name__)

@security_payment_bp.route('/security_payment')
@login_required
def security_payment_page():
    return render_template('security_payment.html')
