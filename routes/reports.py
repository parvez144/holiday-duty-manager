from flask import Blueprint, render_template, request, jsonify, send_file
import mysql.connector
from config import db_config, biotime_config
from datetime import datetime, time, timedelta
from collections import defaultdict
import io
from weasyprint import HTML, CSS
from openpyxl import Workbook
from openpyxl.utils import get_column_letter

reports_bp = Blueprint('reports', __name__)


@reports_bp.route('/reports')
def reports_page():
    return render_template('reports.html')


@reports_bp.route('/api/reports/sub_sections')
def api_sub_sections():
    """Return distinct sub_section list from employees."""
    try:
        conn = mysql.connector.connect(**db_config)
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT Sub_Section FROM employees WHERE Sub_Section IS NOT NULL AND Sub_Section <> '' ORDER BY Sub_Section")
        subs = [r[0] for r in cur.fetchall()]
        return jsonify(subs)
    except Exception as e:
        print('sub_sections error:', e)
        return jsonify([])
    finally:
        try:
            cur.close(); conn.close()
        except Exception:
            pass


@reports_bp.route('/api/reports/categories')
def api_categories():
    """Return distinct category list from employees."""
    try:
        conn = mysql.connector.connect(**db_config)
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT Category FROM employees WHERE Category IS NOT NULL AND Category <> '' ORDER BY Category")
        categories = [r[0] for r in cur.fetchall()]
        return jsonify(categories)
    except Exception as e:
        print('categories error:', e)
        return jsonify([])
    finally:
        try:
            cur.close(); conn.close()
        except Exception:
            pass


def _compute_payment_sheet(for_date: str, sub_section: str | None, category: str | None):
    """Compute payment sheet rows for a given date and optional sub_section.
    
    Uses employee data from mfl_weekend_duty.employees and 
    attendance logs from bio_time.iclock_transaction.
    """
    conn = mysql.connector.connect(**db_config)
    cur = conn.cursor(dictionary=True)
    try:
        # Load employees
        params = []
        conditions = []
        if sub_section:
            conditions.append('Sub_Section = %s')
            params.append(sub_section)
        if category:
            conditions.append('Category = %s')
            params.append(category)
        where = f"WHERE {' AND '.join(conditions)}" if conditions else ''
        
        # Payment rate calculation: (Gross Salary / 30) for daily rate
        cur.execute(
            f"""
            SELECT Emp_Id, Emp_Name, Designation, Sub_Section, Category, Grade,
                   ROUND(Gross_Salary, 0) AS Gross_Salary,
                   ROUND(Gross_Salary / 30, 2) AS Daily_Rate
            FROM employees
            {where}
            ORDER BY Emp_Id
            """,
            params
        )
        employees = cur.fetchall()
        id_to_emp = {str(e['Emp_Id']): e for e in employees}
        if not employees:
            return []

        # Fetch attendance for selected date from bio_time database
        id_list = list(id_to_emp.keys())
        placeholders = ','.join(['%s'] * len(id_list))
        
        att_query = f"""
        SELECT emp_code, punch_time
        FROM bio_time.iclock_transaction
        WHERE DATE(punch_time) = %s
        AND emp_code IN ({placeholders})
        ORDER BY emp_code, punch_time
        """
        
        cur.execute(att_query, [for_date] + id_list)
        att_rows = cur.fetchall()

        # Group times per employee
        times_by_emp = defaultdict(list)
        for r in att_rows:
            times_by_emp[str(r['emp_code'])].append(r['punch_time'])

        rows = []
        serial = 1
        
        for emp_id, emp in id_to_emp.items():
            punches = sorted(times_by_emp.get(emp_id, []))
            
            if not punches:
                continue # Skip if no attendance recorded for this day

            in_dt = punches[0]
            out_dt = punches[-1]
            
            # Duration Calculation
            duration = out_dt - in_dt
            work_hours = duration.total_seconds() / 3600.0
            
            # Payment Logic: Fixed 1 day pay if present
            amount = round(float(emp['Daily_Rate']), 0)

            rows.append({
                'sl': serial,
                'id': emp_id,
                'name': emp['Emp_Name'],
                'designation': emp['Designation'],
                'sub_section': emp['Sub_Section'],
                'gross': float(emp['Gross_Salary']),
                'in_time': in_dt.strftime('%H:%M:%S'),
                'out_time': out_dt.strftime('%H:%M:%S'),
                'hour': round(work_hours, 2),
                'amount': amount,
                'signature': ''
            })
            serial += 1

        return rows
    finally:
        try:
            cur.close(); conn.close()
        except Exception:
            pass


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
    data = request.get_json(silent=True) or {}
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
