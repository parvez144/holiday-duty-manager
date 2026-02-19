from datetime import datetime
from collections import defaultdict
from services.employee_service import get_employees
from services.attendance_service import get_attendance_for_date
from models.designation import Designation

def compute_payment_sheet(for_date: str, section: str | None, sub_section: str | None, category: str | None):
    """Compute payment sheet rows for a given date and optional filters."""
    # 1. Fetch Employees
    employees = get_employees(section=section, sub_section=sub_section, category=category)
    if not employees:
        return []

    # 2. Fetch Attendance
    emp_ids = [str(e['Emp_Id']) for e in employees]
    attendance_data = get_attendance_for_date(for_date, emp_ids)

    rows = []
    serial = 1
    
    for emp in employees:
        emp_id = str(emp['Emp_Id'])
        
        # Skip Security personnel as they don't get holiday payment
        sec = (emp.get('Section') or '').strip().lower()
        sub_sec = (emp.get('Sub_Section') or '').strip().lower()
        if sec == 'security' or sub_sec == 'security':
            continue

        stats = attendance_data.get(emp_id)
        
        if not stats:
            continue # Skip if person has NO punches at all on this day

        # Partitioned Times from Service
        in_dt = stats.get('in_time')
        out_dt = stats.get('out_time')

        # Start Time Rule: Cleaner @ 7:30 AM, Others @ 8:00 AM
        if in_dt:
            is_cleaner = (emp.get('Sub_Section') or '').strip().lower() == 'cleaner'
            start_h, start_m = (7, 30) if is_cleaner else (8, 0)
            start_limit = in_dt.replace(hour=start_h, minute=start_m, second=0, microsecond=0)
            eff_in = max(in_dt, start_limit)
            disp_in = eff_in.strftime('%H:%M')
        else:
            eff_in = None
            disp_in = "Missing"

        # 30-Minute Rounding Down for Out-Time
        if out_dt:
            eff_out = out_dt.replace(minute=(out_dt.minute // 30) * 30, second=0, microsecond=0)
            disp_out = eff_out.strftime('%H:%M')
        else:
            eff_out = None
            disp_out = "Missing"

        # Duration Calculation based on effective times
        if eff_in and eff_out:
            duration = eff_out - eff_in
            raw_hours = duration.total_seconds() / 3600.0
            # Deduct 1 hour for lunch ONLY if working 6 hours or more
            deduction = 1.0 if raw_hours >= 6.0 else 0.0
            work_hours = max(0, raw_hours - deduction)
        else:
            work_hours = 0
        
        # Salary calculations
        gross_salary = float(emp.get('Gross_Salary') or 0)
        # Basic = (Gross - allowances)/1.5
        basic_salary = (gross_salary - 2450) / 1.5
        daily_basic = basic_salary / 30.0
        ot_rate_unit = (basic_salary / 208.0) * 2.0

        emp_cat = (emp.get('Category') or '').strip().lower()
        
        # Robust check to match 'worker', 'workers', 'factory worker' etc.
        if 'worker' in emp_cat:
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
        # User Rule Update: For Staff, 1 punch is enough for amount. 
        # For Workers, 2 punches are required as OT depends on duration.
        if 'Missing' in disp_in or 'Missing' in disp_out:
            if 'worker' in emp_cat:
                amount = 0
                ot_hours = 0
                work_hours = 0
            else:
                # Non-worker (Staff): Single punch is enough to get daily basic.
                if 'Missing' in disp_in and 'Missing' in disp_out:
                    amount = 0
                else:
                    # Amount is already daily_basic
                    pass
                ot_hours = 0
                work_hours = 0

        rows.append({
            'sl': serial,
            'id': emp_id,
            'name': emp['Emp_Name'].title() if emp['Emp_Name'] else '',
            'designation': emp['Designation'].title() if emp['Designation'] else '',
            'sub_section': emp['Sub_Section'].title() if emp['Sub_Section'] else '',
            'section': emp['Section'].title() if emp['Section'] else '',
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

def compute_present_status(for_date: str, section: str | None, sub_section: str | None, category: str | None, status: str = 'all'):
    """Compute present status rows (attendance only) with status filtering."""
    # Ensure for_date is a date object for SQLAlchemy comparison
    if isinstance(for_date, str):
        try:
            for_date_obj = datetime.strptime(for_date, '%Y-%m-%d').date()
        except:
            for_date_obj = for_date
    else:
        for_date_obj = for_date

    print(f"DEBUG: compute_present_status - Date: {for_date_obj}, Status Filter: {status}")

    employees = get_employees(section=section, sub_section=sub_section, category=category)
    if not employees:
        print("DEBUG: No employees found for filters")
        return []

    emp_ids = [str(e['Emp_Id']).strip() for e in employees]
    attendance_data = get_attendance_for_date(for_date_obj, emp_ids)

    rows = []
    serial = 1
    
    for emp in employees:
        emp_id = str(emp['Emp_Id']).strip()
        
        # Skip Security personnel as they are restricted from these reports
        sec = (emp.get('Section') or '').strip().lower()
        sub_sec = (emp.get('Sub_Section') or '').strip().lower()
        if sec == 'security' or sub_sec == 'security':
            continue

        stats = attendance_data.get(emp_id)
        in_dt = stats.get('in_time') if stats else None
        out_dt = stats.get('out_time') if stats else None

        # Determine Status
        emp_status = 'absent'
        if in_dt and out_dt:
            emp_status = 'complete'
        elif in_dt or out_dt:
            emp_status = 'incomplete'
        
        # Apply Status Filter
        if status == 'all':
            # 'all' traditionally means 'present' (at least one punch) in this report
            if emp_status == 'absent':
                continue
        elif status == 'absent':
            if emp_status != 'absent':
                continue
        elif status == 'incomplete':
            if emp_status != 'incomplete':
                continue
        elif status == 'complete':
            if emp_status != 'complete':
                continue

        # Show RAW Times directly from database
        disp_in = in_dt.strftime('%H:%M') if in_dt else "Missing"
        disp_out = out_dt.strftime('%H:%M') if out_dt else " Missing"

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

def compute_night_bill(for_date: str, section: str | None, sub_section: str | None, category: str | None):
    """Compute night bill rows for a given date and optional filters."""
    # 1. Fetch Employees
    employees = get_employees(section=section, sub_section=sub_section, category=category)
    if not employees:
        return []

    # 2. Fetch Attendance
    emp_ids = [str(e['Emp_Id']) for e in employees]
    attendance_data = get_attendance_for_date(for_date, emp_ids)

    rows = []
    serial = 1
    
    for emp in employees:
        emp_id = str(emp['Emp_Id'])
        
        # Skip Security personnel
        sec = (emp.get('Section') or '').strip().lower()
        sub_sec = (emp.get('Sub_Section') or '').strip().lower()
        if sec == 'security' or sub_sec == 'security':
            continue

        stats = attendance_data.get(emp_id)
        if not stats:
            continue

        out_dt = stats.get('out_time')
        if not out_dt:
            continue
            
        emp_cat = (emp.get('Category') or '').strip().lower()
        
        # New Rule: Staff (Non-workers) must work until 11:00 PM (23:00) or later
        # Workers follow the existing rule: At least 30 minutes past 10:00 PM (10:30 PM)
        is_worker = 'worker' in emp_cat
        
        ref_time_10pm = out_dt.replace(hour=22, minute=0, second=0, microsecond=0)
        ref_time_11pm = out_dt.replace(hour=23, minute=0, second=0, microsecond=0)
        
        if not is_worker:
            # Staff Rule
            if out_dt < ref_time_11pm:
                continue
        else:
            # Worker Rule (Current 10:30 PM check)
            if out_dt < ref_time_10pm.replace(minute=30):
                continue
                
        # Total minutes past calculation base (10 PM) for payment computation
        diff = out_dt - ref_time_10pm
        total_minutes = int(diff.total_seconds() / 60)
        
        if total_minutes <= 0:
            continue

        disp_in = stats.get('in_time').strftime('%H:%M') if stats.get('in_time') else "Missing"
        disp_out = out_dt.strftime('%H:%M')
        
        # Duration string for display (H:MM)
        hours_part = total_minutes // 60
        mins_part = total_minutes % 60
        disp_duration = f"{hours_part}:{mins_part:02d}"
        decimal_hours = total_minutes / 60.0

        # Calculation
        designation = (emp.get('Designation') or '').strip().lower()
        
        gross_salary = float(emp.get('Gross_Salary') or 0)
        basic_salary = (gross_salary - 2450) / 1.5
        
        amount = 0
        rate_type = ""
        hourly_rate = 0
        
        if 'worker' in emp_cat:
            # Workers: Based on OT rate (proportional)
            ot_rate_unit = (basic_salary / 208.0) * 2.0
            hourly_rate = ot_rate_unit
            amount = decimal_hours * hourly_rate
            rate_type = "OT Rate"
        else:
            # Staff: Fixed amount based on Designation (NOT proportional)
            # Fetch from the relationship object passed by employee_service
            desig_obj = emp.get('designation_obj')
            if desig_obj:
                amount = desig_obj.night_bill
            else:
                # Fallback if relationship not loaded (should not happen with updated service)
                amount = 0
            
            hourly_rate = amount # For display in 'Rate' column
            rate_type = "Fixed Rate"

        if amount > 0:
            rows.append({
                'sl': serial,
                'id': emp_id,
                'name': emp['Emp_Name'].title() if emp['Emp_Name'] else '',
                'designation': emp['Designation'].title() if emp['Designation'] else '',
                'sub_section': emp['Sub_Section'].title() if emp['Sub_Section'] else '',
                'section': emp['Section'].title() if emp['Section'] else '',
                'category': emp.get('Category', ''),
                'gross': round(gross_salary, 0),
                'basic': round(basic_salary, 0),
                'hour': disp_duration,
                'decimal_hour': round(decimal_hours, 2),
                'rate': round(hourly_rate, 2),
                'in_time': disp_in,
                'out_time': disp_out,
                'rate_type': rate_type,
                'amount': round(amount, 0),
                'remarks': '',
                'signature': ''
            })
            serial += 1

    return rows

def compute_security_payment(for_date: str):
    """Compute holiday payment for security personnel (double basic for any attendance)."""
    # 1. Fetch Employees in Security Subsection
    employees = get_employees(sub_section='Security')
    if not employees:
        return []

    # 2. Fetch Attendance
    emp_ids = [str(e['Emp_Id']) for e in employees]
    attendance_data = get_attendance_for_date(for_date, emp_ids)

    rows = []
    serial = 1
    
    for emp in employees:
        emp_id = str(emp['Emp_Id'])
        stats = attendance_data.get(emp_id)
        
        # Security Rule: If ANY punch exists, they get paid
        if not stats:
            continue

        in_dt = stats.get('in_time')
        out_dt = stats.get('out_time')
        
        # Display times
        disp_in = in_dt.strftime('%H:%M') if in_dt else "Missing"
        disp_out = out_dt.strftime('%H:%M') if out_dt else "Missing"

        # Salary calculations
        gross_salary = float(emp.get('Gross_Salary') or 0)
        # Basic = (Gross - allowances)/1.5
        basic_salary = (gross_salary - 2450) / 1.5
        daily_basic = basic_salary / 30.0
        
        # Rule: Double Daily Basic
        amount = daily_basic * 2.0

        rows.append({
            'sl': serial,
            'id': emp_id,
            'name': emp['Emp_Name'].title() if emp['Emp_Name'] else '',
            'designation': emp['Designation'].title() if emp['Designation'] else '',
            'sub_section': emp['Sub_Section'].title() if emp['Sub_Section'] else '',
            'section': emp['Section'].title() if emp['Section'] else '',
            'gross': gross_salary,
            'basic': round(basic_salary, 0),
            'in_time': disp_in,
            'out_time': disp_out,
            'amount': round(amount, 0),
            'remarks': '',
            'signature': ''
        })
        serial += 1

    return rows
