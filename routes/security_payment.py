from flask import Blueprint, render_template, request, send_file
from flask_login import login_required
from services.report_service import compute_security_payment, get_holiday_records
from models.holiday import Holiday
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
    
    rows = []
    is_holiday_mode = False
    holiday_name = None
    
    # Check if single date and if it's a holiday with processed data
    if start_date == end_date:
        try:
            target_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            holiday = Holiday.query.filter_by(holiday_date=target_date).first()
            if holiday and holiday.processed_at:
                # Security is stored with sub_section='Security' or section='Security'
                # get_holiday_records returns filtered snapshotted data
                rows = get_holiday_records(holiday.id, sub_section='Security', include_security=True)
                is_holiday_mode = True
                holiday_name = holiday.holiday_name
        except Exception as e:
            print(f"Error checking holiday snapshot: {e}")
    
    if not is_holiday_mode:
        rows = compute_security_payment(start_date, end_date)
        
    return render_template(
        'security_payment.html', 
        rows=rows, 
        start_date=start_date, 
        end_date=end_date, 
        is_holiday_mode=is_holiday_mode,
        holiday_name=holiday_name,
        datetime=datetime
    )

@security_payment_bp.route('/security_payment/pdf')
@login_required
def security_payment_pdf():
    today = datetime.today().strftime('%Y-%m-%d')
    start_date = request.args.get('start_date', today)
    end_date = request.args.get('end_date', today)
    
    rows = []
    is_holiday_mode = False
    holiday_name = None
    
    # Check if single date and if it's a holiday with processed data
    if start_date == end_date:
        try:
            target_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            holiday = Holiday.query.filter_by(holiday_date=target_date).first()
            if holiday and holiday.processed_at:
                rows = get_holiday_records(holiday.id, sub_section='Security', include_security=True)
                is_holiday_mode = True
                holiday_name = holiday.holiday_name
        except Exception as e:
            print(f"Error checking holiday snapshot: {e}")
            
    if not is_holiday_mode:
        rows = compute_security_payment(start_date, end_date)
    
    html_content = render_template(
        'security_payment_pdf.html',
        start_date=start_date,
        end_date=end_date,
        is_holiday_mode=is_holiday_mode,
        holiday_name=holiday_name,
        rows=rows,
        datetime=datetime
    )

    pdf_buffer = io.BytesIO()
    HTML(string=html_content, base_url=request.url_root).write_pdf(pdf_buffer)
    pdf_buffer.seek(0)
    return send_file(pdf_buffer, as_attachment=False, mimetype='application/pdf')
