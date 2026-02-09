from models.employee import Employee
from extensions import db
from sqlalchemy import distinct

def get_employees(sub_section=None, category=None):
    """
    Fetches employees based on optional sub_section and category filters.
    
    :param sub_section: Optional sub-section to filter by.
    :param category: Optional category to filter by.
    :return: List of employee dictionaries (or objects, but keeping dicts for compatibility with reports.py).
    """
    query = Employee.query

    if sub_section:
        query = query.filter(Employee.Sub_Section == sub_section)
    if category:
        query = query.filter(Employee.Category == category)
    
    # Selecting specific columns to match previous behavior, or just return objects.
    # The report expects dicts with specific keys. SQLAlchemy models return objects.
    # We can stick to objects and access attributes, OR convert to dicts.
    # Let's see reports.py usage: emp['Emp_Id'], emp['Emp_Name']...
    # So we should convert to dicts or return objects that look like dicts?
    # Actually, if we return objects, we need to change reports.py to use dot notation.
    # To minimize changes in reports.py, let's return a list of dictionaries for now.
    
    employees = query.order_by(Employee.Emp_Id).all()
    
    result = []
    for emp in employees:
        # Calculate daily rate as per previous logic (Gross_Salary / 30)
        daily_rate = round(float(emp.Gross_Salary or 0) / 30, 2)
        
        result.append({
            'Emp_Id': emp.Emp_Id,
            'Emp_Name': emp.Emp_Name,
            'Designation': emp.Designation,
            'Sub_Section': emp.Sub_Section,
            'Category': emp.Category,
            'Grade': emp.Grade,
            'Gross_Salary': float(emp.Gross_Salary or 0),
            'Daily_Rate': daily_rate
        })
    return result

def get_distinct_sub_sections():
    """Returns a list of distinct sub-sections."""
    # SQLAlchemy: db.session.query(distinct(Employee.Sub_Section))
    results = db.session.query(distinct(Employee.Sub_Section)).filter(Employee.Sub_Section != None, Employee.Sub_Section != '').order_by(Employee.Sub_Section).all()
    return [r[0] for r in results]

def get_distinct_categories():
    """Returns a list of distinct categories."""
    results = db.session.query(distinct(Employee.Category)).filter(Employee.Category != None, Employee.Category != '').order_by(Employee.Category).all()
    return [r[0] for r in results]
