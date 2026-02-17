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
            punch, status = add_manual_punch(emp_code, punch_time)
            
            if status == "updated":
                flash(f'Manual punch updated for {emp_code} at {punch_time.strftime("%I:%M %p")}', 'success')
            else:
                flash(f'Manual punch added for {emp_code} at {punch_time.strftime("%I:%M %p")}', 'success')
        except Exception as e:
            flash(f'Error saving punch: {str(e)}', 'danger')
            
        return redirect(url_for('attendance_mgmt.manual_entry'))

    employees = get_employees()
    
    # Fetch recent manual entries
    from models.attendance import IClockTransaction
    recent_entries = IClockTransaction.query.filter_by(is_corrected=True).order_by(IClockTransaction.updated_at.desc()).limit(10).all()
    
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('manual_attendance.html', employees=employees, today=today, recent_entries=recent_entries)

@attendance_mgmt_bp.route('/attendance/manual/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_manual_punch(id):
    from models.attendance import IClockTransaction
    punch = IClockTransaction.query.get(id)
    if punch and punch.is_corrected:
        try:
            db.session.delete(punch)
            db.session.commit()
            flash('Manual punch deleted successfully.', 'success')
        except Exception as e:
            flash(f'Error deleting punch: {str(e)}', 'danger')
    else:
        flash('Punch record not found or not a manual entry.', 'danger')
    return redirect(url_for('attendance_mgmt.manual_entry'))

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
