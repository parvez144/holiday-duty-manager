from app import app
from services.employee_service import get_employees
from services.attendance_service import get_attendance_for_date

def _compute_payment_sheet_debug(for_date: str, sub_section: str | None, category: str | None):
    with app.app_context():
        # 1. Fetch Employees
        employees = get_employees(sub_section, category)
        print(f"DEBUG: Found {len(employees)} employees")
        
        emp_ids = [str(e['Emp_Id']) for e in employees]
        attendance_data = get_attendance_for_date(for_date, emp_ids)
        print(f"DEBUG: Found {len(attendance_data)} attendance records")

        for emp in employees:
            emp_id = str(emp['Emp_Id'])
            stats = attendance_data.get(emp_id)
            
            if not stats:
                continue

            in_dt = stats['in_time']
            out_dt = stats['out_time']

            # Partitioned Logic from Service is already used here via get_attendance_for_date
            # But let's verify the display and pay logic from reports.py
            
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
                deduction = 1.0 if raw_hours >= 6.0 else 0.0
                work_hours = max(0, raw_hours - deduction)
            else:
                work_hours = 0
            
            # Salary calculations
            gross_salary = float(emp.get('Gross_Salary') or 0)
            basic_salary = (gross_salary - 2450) / 1.5
            daily_basic = basic_salary / 30.0

            category = (emp.get('Category') or '').strip().lower()
            
            if 'worker' in category:
                amount = work_hours * ((basic_salary / 208.0) * 2.0)
            else:
                amount = daily_basic

            # Force 0 amount if any punch is missing
            if disp_in == "Missing" or disp_out == "Missing":
                if work_hours > 0 or amount > 0:
                    print(f"DEBUG: ID={emp_id} ZEROED OUT. In: {disp_in}, Out: {disp_out}")
                amount = 0
            
            if amount > 0:
                print(f"DEBUG: ID={emp_id} VALID Amount: {amount} (Hrs: {work_hours}) In: {disp_in}, Out: {disp_out}")

if __name__ == "__main__":
    _compute_payment_sheet_debug('2025-12-10', None, None)
