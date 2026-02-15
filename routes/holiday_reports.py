from flask import Blueprint, render_template, request, jsonify, send_file
from flask_login import login_required
from services.report_service import compute_payment_sheet, compute_present_status
from datetime import datetime
from collections import defaultdict
import io
import json
from weasyprint import HTML
from openpyxl import Workbook
from openpyxl.utils import get_column_letter

holiday_reports_bp = Blueprint('holiday_reports', __name__)

@holiday_reports_bp.route('/reports')
@login_required
def reports_page():
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('reports.html', today=today)

@holiday_reports_bp.route('/present_status')
@login_required
def present_status_page():
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('present_filter.html', today=today)

@holiday_reports_bp.route('/api/reports/payment_sheet', methods=['POST'])
@login_required
def api_payment_sheet():
    data = request.get_json(silent=True) or {}
    for_date = data.get('date')
    section = data.get('section')
    sub_section = data.get('sub_section')
    category = data.get('category')
    if not for_date:
        return jsonify({'error': 'date is required (YYYY-MM-DD)'}), 400
    try:
        rows = compute_payment_sheet(for_date, section, sub_section, category)
        return jsonify({'date': for_date, 'section': section, 'sub_section': sub_section, 'category': category, 'rows': rows})
    except Exception as e:
        print('payment_sheet error:', e)
        return jsonify({'error': f'failed to compute: {str(e)}'}), 500

@holiday_reports_bp.route('/api/reports/present_status', methods=['POST'])
@login_required
def api_present_status():
    data = request.get_json(silent=True) or {}
    for_date = data.get('date')
    section = data.get('section')
    sub_section = data.get('sub_section')
    category = data.get('category')
    if not for_date:
        return jsonify({'error': 'date is required'}), 400
    try:
        rows = compute_present_status(for_date, section, sub_section, category)
        return jsonify({'date': for_date, 'rows': rows})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@holiday_reports_bp.route('/reports/payment_sheet/pdf', methods=['POST'])
@login_required
def payment_sheet_pdf():
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
    
    rows = compute_payment_sheet(for_date, section, sub_section, category)
    
    grouped_rows = defaultdict(list)
    for r in rows:
        sec_name = (r.get('section') or 'Unknown').strip()
        grouped_rows[sec_name].append(r)

    html_content = render_template(
        'payment_sheet_pdf.html',
        for_date=for_date,
        grouped_rows=grouped_rows,
        datetime=datetime
    )

    pdf_buffer = io.BytesIO()
    HTML(string=html_content, base_url=request.url_root).write_pdf(pdf_buffer)
    pdf_buffer.seek(0)
    return send_file(pdf_buffer, as_attachment=False, mimetype='application/pdf')

@holiday_reports_bp.route('/reports/present_status/pdf', methods=['POST'])
@login_required
def present_status_pdf():
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
    
    rows = compute_present_status(for_date, section, sub_section, category)
    
    grouped_rows = defaultdict(list)
    for r in rows:
        sec_name = (r.get('section') or 'Unknown').strip()
        grouped_rows[sec_name].append(r)

    html_content = render_template(
        'present_status.html',
        for_date=for_date,
        grouped_rows=grouped_rows,
        datetime=datetime
    )

    pdf_buffer = io.BytesIO()
    HTML(string=html_content, base_url=request.url_root).write_pdf(pdf_buffer)
    pdf_buffer.seek(0)
    return send_file(pdf_buffer, as_attachment=False, mimetype='application/pdf')

@holiday_reports_bp.route('/reports/payment_sheet/excel', methods=['POST'])
@login_required
def payment_sheet_excel():
    data = request.get_json(silent=True) or {}
    for_date = data.get('date')
    section = data.get('section')
    sub_section = data.get('sub_section')
    category = data.get('category')
    if not for_date:
        return jsonify({'error': 'date is required'}), 400
    
    rows = compute_payment_sheet(for_date, section, sub_section, category)

    wb = Workbook()
    ws = wb.active
    ws.title = 'Payment Sheet'
    headers = ['SL', 'ID', 'Name', 'Designation', 'Section', 'Gross', 'Basic', 'In Time', 'Out Time', 'Amount', 'Signature']
    ws.append(headers)
    for r in rows:
        ws.append([
            r['sl'], r['id'], r['name'], r['designation'], r['section'], r['gross'], round(r['basic'], 0), r['in_time'], r['out_time'], r['amount'], ''
        ])
    
    for col in range(1, len(headers) + 1):
        ws.column_dimensions[get_column_letter(col)].width = 16

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return send_file(io.BytesIO(buf.getvalue()), as_attachment=True,
                     download_name=f'payment_sheet_{for_date}.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
