from flask import Blueprint, render_template, request, send_file
from flask_login import login_required
from services.report_service import compute_security_payment
from datetime import datetime
import io
from weasyprint import HTML

security_payment_bp = Blueprint('security_payment', __name__)

@security_payment_bp.route('/security_payment')
@login_required
def security_payment_page():
    for_date = request.args.get('date', datetime.today().strftime('%Y-%m-%d'))
    rows = compute_security_payment(for_date)
    return render_template('security_payment.html', rows=rows, for_date=for_date, datetime=datetime)

@security_payment_bp.route('/security_payment/pdf')
@login_required
def security_payment_pdf():
    for_date = request.args.get('date', datetime.today().strftime('%Y-%m-%d'))
    rows = compute_security_payment(for_date)
    
    html_content = render_template(
        'security_payment_pdf.html',
        for_date=for_date,
        rows=rows,
        datetime=datetime
    )

    pdf_buffer = io.BytesIO()
    HTML(string=html_content, base_url=request.url_root).write_pdf(pdf_buffer)
    pdf_buffer.seek(0)
    return send_file(pdf_buffer, as_attachment=False, mimetype='application/pdf')
