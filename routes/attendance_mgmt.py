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

@attendance_mgmt_bp.route('/api/attendance/missing')
@login_required
def get_missing_punches():
    date_str = request.args.get('date')
    if not date_str:
        return jsonify({'error': 'Missing date parameter'}), 400
        
    try:
        from services.attendance_service import get_attendance_for_date
        attendance = get_attendance_for_date(date_str)
        
        missing_list = []
        for emp_code, data in attendance.items():
            has_in = data.get('in_time') is not None
            has_out = data.get('out_time') is not None
            
            # User rule: Only those with exactly one punch are "incomplete"
            if (has_in and not has_out) or (has_out and not has_in):
                missing_list.append({
                    'emp_code': str(emp_code).strip(),
                    'in_time': data.get('in_time').strftime('%H:%M') if has_in else '',
                    'out_time': data.get('out_time').strftime('%H:%M') if has_out else '',
                    'missing_type': 'Missing Out' if has_in else 'Missing In'
                })
        
        employees = get_employees()
        emp_dict = {str(emp['Emp_Id']).strip(): emp for emp in employees}
        
        for item in missing_list:
            emp_info = emp_dict.get(item['emp_code'])
            if emp_info:
                item['emp_name'] = emp_info['Emp_Name']
                item['section'] = emp_info['Section']
            else:
                item['emp_name'] = 'Unknown'
                item['section'] = 'Unknown'
                
        missing_list.sort(key=lambda x: x['emp_code'])
                
        return jsonify(missing_list)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@attendance_mgmt_bp.route('/attendance/manual/bulk', methods=['POST'])
@login_required
@admin_required
def manual_entry_bulk():
    data = request.json
    if not data or not isinstance(data, list):
        return jsonify({'success': False, 'message': 'Invalid data format'}), 400
        
    try:
        added_count = 0
        for entry in data:
            emp_code = entry.get('emp_code')
            date_str = entry.get('date')
            in_time = entry.get('in_time')
            out_time = entry.get('out_time')
            
            if not emp_code or not date_str:
                continue
                
            if in_time:
                punch_in = datetime.strptime(f"{date_str} {in_time}", '%Y-%m-%d %H:%M')
                add_manual_punch(emp_code, punch_in)
                added_count += 1
                
            if out_time:
                punch_out = datetime.strptime(f"{date_str} {out_time}", '%Y-%m-%d %H:%M')
                add_manual_punch(emp_code, punch_out)
                added_count += 1
                
        return jsonify({'success': True, 'message': f'Successfully updated {added_count} manual punches.'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
