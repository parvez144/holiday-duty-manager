from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from services.attendance_service import add_manual_punch
from services.employee_service import get_employees
from datetime import datetime
from routes.auth import admin_required

attendance_mgmt_bp = Blueprint('attendance_mgmt', __name__)

@attendance_mgmt_bp.route('/attendance/manual', methods=['GET', 'POST'])
@login_required
@admin_required
def manual_entry():
    if request.method == 'POST':
        emp_code = request.form.get('emp_code')
        date_str = request.form.get('date')
        time_str = request.form.get('time')
        
        if not emp_code or not date_str or not time_str:
            flash('All fields are required.', 'danger')
            return redirect(url_for('attendance_mgmt.manual_entry'))
            
        try:
            punch_time = datetime.strptime(f"{date_str} {time_str}", '%Y-%m-%d %H:%M')
            add_manual_punch(emp_code, punch_time)
            flash(f'Manual punch added for {emp_code} at {punch_time.strftime("%Y-%m-%d %I:%M %p")}', 'success')
        except Exception as e:
            flash(f'Error adding punch: {str(e)}', 'danger')
            
        return redirect(url_for('attendance_mgmt.manual_entry'))

    employees = get_employees()
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('manual_attendance.html', employees=employees, today=today)

@attendance_mgmt_bp.route('/api/attendance/status')
@login_required
def get_attendance_status():
    emp_code = request.args.get('emp_code')
    date_str = request.args.get('date')
    
    if not emp_code or not date_str:
        return jsonify({'error': 'Missing parameters'}), 400
        
    try:
        from services.attendance_service import get_attendance_for_date
        attendance = get_attendance_for_date(date_str, [emp_code])
        data = attendance.get(emp_code, {'in_time': None, 'out_time': None})
        
        return jsonify({
            'in_time': data['in_time'].strftime('%H:%M') if data['in_time'] else "Missing",
            'out_time': data['out_time'].strftime('%H:%M') if data['out_time'] else "Missing"
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
