from flask import Blueprint, render_template, request, jsonify, send_file
from flask_login import login_required
from services.report_service import compute_night_bill
from datetime import datetime
from collections import defaultdict
import io
import json
from weasyprint import HTML

night_bill_bp = Blueprint('night_bill', __name__)

@night_bill_bp.route('/night_bill')
@login_required
def night_bill_page():
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('night_bill.html', today=today)

@night_bill_bp.route('/api/night_bill', methods=['POST'])
@login_required
def api_night_bill():
    data = request.get_json(silent=True) or {}
    for_date = data.get('date')
    section = data.get('section')
    sub_section = data.get('sub_section')
    category = data.get('category')
    if not for_date:
        return jsonify({'error': 'date is required'}), 400
    try:
        rows = compute_night_bill(for_date, section, sub_section, category)
        return jsonify({'date': for_date, 'rows': rows})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@night_bill_bp.route('/night_bill/pdf', methods=['POST'])
@login_required
def night_bill_pdf():
    if request.is_json:
        data = request.get_json(silent=True) or {}
    else:
        form_data = request.form.get('data')
        data = json.loads(form_data) if form_data else {}
    
    for_date = data.get('date')
    section = data.get('section')
    sub_section = data.get('sub_section')
    category = data.get('category')
    if not for_date:
        return jsonify({'error': 'date is required'}), 400
    
    rows = compute_night_bill(for_date, section, sub_section, category)
    
    grouped_rows = defaultdict(list)
    for r in rows:
        sec_name = (r.get('section') or 'All').strip()
        grouped_rows[sec_name].append(r)

    html_content = render_template(
        'night_bill_pdf.html',
        for_date=for_date,
        grouped_rows=grouped_rows,
        datetime=datetime
    )

    pdf_buffer = io.BytesIO()
    HTML(string=html_content, base_url=request.url_root).write_pdf(pdf_buffer)
    pdf_buffer.seek(0)
    return send_file(pdf_buffer, as_attachment=False, mimetype='application/pdf')
