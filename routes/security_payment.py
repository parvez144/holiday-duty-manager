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
    today = datetime.today().strftime('%Y-%m-%d')
    start_date = request.args.get('start_date', today)
    end_date = request.args.get('end_date', today)
    
    rows = compute_security_payment(start_date, end_date)
    return render_template(
        'security_payment.html', 
        rows=rows, 
        start_date=start_date, 
        end_date=end_date, 
        datetime=datetime
    )

@security_payment_bp.route('/security_payment/pdf')
@login_required
def security_payment_pdf():
    today = datetime.today().strftime('%Y-%m-%d')
    start_date = request.args.get('start_date', today)
    end_date = request.args.get('end_date', today)
    
    rows = compute_security_payment(start_date, end_date)
    
    html_content = render_template(
        'security_payment_pdf.html',
        start_date=start_date,
        end_date=end_date,
        rows=rows,
        datetime=datetime
    )

    pdf_buffer = io.BytesIO()
    HTML(string=html_content, base_url=request.url_root).write_pdf(pdf_buffer)
    pdf_buffer.seek(0)
    return send_file(pdf_buffer, as_attachment=False, mimetype='application/pdf')
