from flask import Blueprint, render_template, request, jsonify, send_file
from services.employee_service import get_employees, get_distinct_sub_sections, get_distinct_categories
from services.attendance_service import get_attendance_for_date
from datetime import datetime
from collections import defaultdict
import io
from weasyprint import HTML
from openpyxl import Workbook
from openpyxl.utils import get_column_letter

reports_bp = Blueprint('reports', __name__)


@reports_bp.route('/reports')
def reports_page():
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('reports.html', today=today)


@reports_bp.route('/api/reports/sub_sections')
def api_sub_sections():
    """Return distinct sub_section list from employees."""
    return jsonify(get_distinct_sub_sections())


@reports_bp.route('/api/reports/categories')
def api_categories():
    """Return distinct category list from employees."""
    return jsonify(get_distinct_categories())


def _compute_payment_sheet(for_date: str, sub_section: str | None, category: str | None):
    """Compute payment sheet rows for a given date and optional sub_section.
    
    Uses employee data from employee_service and 
    attendance logs from attendance_service.
    """
    # 1. Fetch Employees
    employees = get_employees(sub_section, category)
    if not employees:
        return []

    # 2. Fetch Attendance
    # We can optimize by passing IDs, or just fetch all for the day if the list is huge.
    # Given the implementation, passing IDs is safer for filtering.
    emp_ids = [str(e['Emp_Id']) for e in employees]
    attendance_data = get_attendance_for_date(for_date, emp_ids)

    rows = []
    serial = 1
    
    for emp in employees:
        emp_id = str(emp['Emp_Id'])
        stats = attendance_data.get(emp_id)
        
        if not stats or not stats['in_time'] or not stats['out_time']:
            continue # Skip if no complete attendance recorded for this day

        in_dt = stats['in_time']
        out_dt = stats['out_time']
        
        # Duration Calculation
        duration = out_dt - in_dt
        work_hours = duration.total_seconds() / 3600.0
        
        # Salary calculations
        gross_salary = float(emp['Gross_Salary'])
        # Basic = (Gross - allowances)/1.5
        basic_salary = (gross_salary-2450)/1.5
        
        # OT calculation: assuming standard 8 hours, anything beyond is OT
        standard_hours = 8.0
        ot_hours = max(0, work_hours - standard_hours)
        
        # OT Rate calculation: (Basic / 208) * 2
        # 208 = standard monthly working hours (26 days * 8 hours)
        ot_rate = (basic_salary / 208.0) * 2.0 if ot_hours > 0 else 0
        
        # Payment Logic: Basic daily rate + OT amount
        daily_basic = basic_salary / 26.0  # Assuming 26 working days per month
        ot_amount = ot_hours * ot_rate
        amount = daily_basic + ot_amount

        rows.append({
            'sl': serial,
            'id': emp_id,
            'name': emp['Emp_Name'],
            'designation': emp['Designation'],
            'sub_section': emp['Sub_Section'],
            'gross': gross_salary,
            'basic': basic_salary,
            'in_time': in_dt.strftime('%H:%M:%S'),
            'out_time': out_dt.strftime('%H:%M:%S'),
            'hour': round(work_hours, 2),
            'ot': ot_hours,
            'ot_rate': ot_rate,
            'amount': round(amount, 0),
            'signature': ''
        })
        serial += 1

    return rows


@reports_bp.route('/api/reports/payment_sheet', methods=['POST'])
def api_payment_sheet():
    data = request.get_json(silent=True) or {}
    for_date = data.get('date')
    sub_section = data.get('sub_section')
    category = data.get('category')
    if not for_date:
        return jsonify({'error': 'date is required (YYYY-MM-DD)'}), 400
    try:
        rows = _compute_payment_sheet(for_date, sub_section, category)
        return jsonify({'date': for_date, 'sub_section': sub_section, 'category': category, 'rows': rows})
    except Exception as e:
        print('payment_sheet error:', e)
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'failed to compute: {str(e)}'}), 500


@reports_bp.route('/reports/payment_sheet/pdf', methods=['POST'])
def payment_sheet_pdf():
    # Accept both JSON and form data
    if request.is_json:
        data = request.get_json(silent=True) or {}
    else:
        # Handle form data
        form_data = request.form.get('data')
        if form_data:
            import json
            data = json.loads(form_data)
        else:
            data = {}
    
    for_date = data.get('date')
    sub_section = data.get('sub_section')
    category = data.get('category')
    if not for_date:
        return jsonify({'error': 'date is required'}), 400
    
    rows = _compute_payment_sheet(for_date, sub_section, category)
    
    grouped_rows = defaultdict(list)
    for r in rows:
        section = (r.get('sub_section') or 'Unknown').strip()
        grouped_rows[section].append(r)

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


@reports_bp.route('/reports/payment_sheet/excel', methods=['POST'])
def payment_sheet_excel():
    data = request.get_json(silent=True) or {}
    for_date = data.get('date')
    sub_section = data.get('sub_section')
    category = data.get('category')
    if not for_date:
        return jsonify({'error': 'date is required'}), 400
    
    rows = _compute_payment_sheet(for_date, sub_section, category)

    wb = Workbook()
    ws = wb.active
    ws.title = 'Payment Sheet'
    headers = ['SL', 'ID', 'Name', 'Designation', 'Gross', 'In Time', 'Out Time', 'Hour', 'Amount', 'Signature']
    ws.append(headers)
    for r in rows:
        ws.append([
            r['sl'], r['id'], r['name'], r['designation'], r['gross'], r['in_time'], r['out_time'], r['hour'], r['amount'], ''
        ])
    
    for col in range(1, len(headers) + 1):
        ws.column_dimensions[get_column_letter(col)].width = 16

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return send_file(io.BytesIO(buf.getvalue()), as_attachment=True,
                     download_name=f'payment_sheet_{for_date}.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
