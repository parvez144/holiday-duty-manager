from flask import Blueprint, render_template, request, jsonify, send_file
from services.employee_service import get_employees, get_distinct_sub_sections, get_distinct_categories
from services.attendance_service import get_attendance_for_date
from datetime import datetime
from collections import defaultdict
import io
import json
from weasyprint import HTML
from openpyxl import Workbook
from openpyxl.utils import get_column_letter

reports_bp = Blueprint('reports', __name__)


@reports_bp.route('/reports')
def reports_page():
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('reports.html', today=today)


@reports_bp.route('/present_status')
def present_status_page():
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('present_filter.html', today=today)


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

        # Start Time Rule: Cleaner @ 7:30 AM, Others @ 8:00 AM
        is_cleaner = (emp.get('Sub_Section') or '').strip().lower() == 'cleaner'
        start_h, start_m = (7, 30) if is_cleaner else (8, 0)
        start_limit = in_dt.replace(hour=start_h, minute=start_m, second=0, microsecond=0)
        eff_in = max(in_dt, start_limit)

        # 30-Minute Rounding Down for Out-Time
        eff_out = out_dt.replace(minute=(out_dt.minute // 30) * 30, second=0, microsecond=0)

        # In-Time Validation: Missing if >= 1 PM (13:00)
        if eff_in.hour >= 13:
            disp_in = "Missing"
        else:
            disp_in = eff_in.strftime('%H:%M')

        # Out-Time Validation: Missing if < 2 PM (14:00)
        if eff_out and eff_out.hour >= 14:
            disp_out = eff_out.strftime('%H:%M')
        else:
            disp_out = " Missing"

        # Duration Calculation based on effective times
        duration = eff_out - eff_in
        raw_hours = duration.total_seconds() / 3600.0
        
        # Deduct 1 hour for lunch ONLY if working 6 hours or more
        deduction = 1.0 if raw_hours >= 6.0 else 0.0
        work_hours = max(0, raw_hours - deduction)
        
        # Salary calculations
        gross_salary = float(emp.get('Gross_Salary') or 0)
        # Basic = (Gross - allowances)/1.5
        basic_salary = (gross_salary - 2450) / 1.5
        daily_basic = basic_salary / 30.0
        ot_rate_unit = (basic_salary / 208.0) * 2.0

        category = (emp.get('Category') or '').strip().lower()
        
        # Robust check to match 'worker', 'workers', 'factory worker' etc.
        if 'worker' in category:
            # Workers: Entire duration as OT
            ot_hours = work_hours
            ot_rate = ot_rate_unit
            amount = ot_hours * ot_rate
        else:
            # Staff and others: One day basic money
            ot_hours = 0
            ot_rate = ot_rate_unit
            amount = daily_basic

        # Force 0 amount if any punch is missing/invalid
        if 'Missing' in disp_in or 'Missing' in disp_out:
            amount = 0
            ot_hours = 0
            work_hours = 0

        rows.append({
            'sl': serial,
            'id': emp_id,
            'name': emp['Emp_Name'].title() if emp['Emp_Name'] else '',
            'designation': emp['Designation'].title() if emp['Designation'] else '',
            'sub_section': emp['Sub_Section'].title() if emp['Sub_Section'] else '',
            'category': emp.get('Category', ''),
            'gross': gross_salary,
            'basic': round(basic_salary, 0),
            'in_time': disp_in,
            'out_time': disp_out,
            'hour': round(work_hours, 2),
            'ot': round(ot_hours, 2),
            'ot_rate': round(ot_rate, 2),
            'amount': round(amount, 0),
            'remarks': '',
            'signature': ''
        })
        serial += 1

    return rows


def _compute_present_status(for_date: str, sub_section: str | None, category: str | None):
    """Compute present status rows (attendance only)."""
    employees = get_employees(sub_section, category)
    if not employees:
        return []

    emp_ids = [str(e['Emp_Id']) for e in employees]
    attendance_data = get_attendance_for_date(for_date, emp_ids)

    rows = []
    serial = 1
    
    for emp in employees:
        emp_id = str(emp['Emp_Id'])
        stats = attendance_data.get(emp_id)
        
        # In this report, skip only if no IN time? 
        # Or same logic as payment sheet? Usually present means at least an In time.
        if not stats or not stats['in_time']:
            continue

        in_dt = stats['in_time']
        out_dt = stats['out_time']

        # Start Time Rule: Cleaner @ 7:30 AM, Others @ 8:00 AM
        is_cleaner = (emp.get('Sub_Section') or '').strip().lower() == 'cleaner'
        start_h, start_m = (7, 30) if is_cleaner else (8, 0)
        start_limit = in_dt.replace(hour=start_h, minute=start_m, second=0, microsecond=0)
        eff_in = max(in_dt, start_limit)

        # 30-Minute Rounding Down for Out-Time
        if out_dt:
            eff_out = out_dt.replace(minute=(out_dt.minute // 30) * 30, second=0, microsecond=0)
        else:
            eff_out = None

        # In-Time Validation: Missing if >= 1 PM (13:00)
        if eff_in.hour >= 13:
            disp_in = "Missing"
        else:
            disp_in = eff_in.strftime('%H:%M')

        # Out-Time Validation: Missing if < 2 PM (14:00)
        # Using >= 14 for "after 2 PM" logic
        if eff_out and eff_out.hour >= 14:
            disp_out = eff_out.strftime('%H:%M')
        else:
            disp_out = " Missing"

        rows.append({
            'sl': serial,
            'id': emp_id,
            'name': emp['Emp_Name'].title() if emp['Emp_Name'] else '',
            'designation': emp['Designation'].title() if emp['Designation'] else '',
            'sub_section': emp['Sub_Section'].title() if emp['Sub_Section'] else '',
            'in_time': disp_in,
            'out_time': disp_out,
            'remarks': ''
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


@reports_bp.route('/api/reports/present_status', methods=['POST'])
def api_present_status():
    data = request.get_json(silent=True) or {}
    for_date = data.get('date')
    sub_section = data.get('sub_section')
    category = data.get('category')
    if not for_date:
        return jsonify({'error': 'date is required'}), 400
    try:
        rows = _compute_present_status(for_date, sub_section, category)
        return jsonify({'date': for_date, 'rows': rows})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@reports_bp.route('/reports/present_status/pdf', methods=['POST'])
def present_status_pdf():
    # Handle both JSON and form data
    if request.is_json:
        data = request.get_json(silent=True) or {}
    else:
        form_data = request.form.get('data')
        data = json.loads(form_data) if form_data else {}
    
    for_date = data.get('date')
    sub_section = data.get('sub_section')
    category = data.get('category')
    
    if not for_date:
        return jsonify({'error': 'date is required'}), 400
    
    rows = _compute_present_status(for_date, sub_section, category)
    
    grouped_rows = defaultdict(list)
    for r in rows:
        section = (r.get('sub_section') or 'Unknown').strip()
        grouped_rows[section].append(r)

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
    headers = ['SL', 'ID', 'Name', 'Designation', 'Sub Section', 'Gross', 'Basic', 'In Time', 'Out Time', 'Amount', 'Signature']
    ws.append(headers)
    for r in rows:
        ws.append([
            r['sl'], r['id'], r['name'], r['designation'], r['sub_section'], r['gross'], round(r['basic'], 0), r['in_time'], r['out_time'], r['amount'], ''
        ])
    
    for col in range(1, len(headers) + 1):
        ws.column_dimensions[get_column_letter(col)].width = 16

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return send_file(io.BytesIO(buf.getvalue()), as_attachment=True,
                     download_name=f'payment_sheet_{for_date}.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
