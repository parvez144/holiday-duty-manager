from models.employee import Employee
from extensions import db
from sqlalchemy import distinct

def get_employees(section=None, sub_section=None, category=None):
    """
    Fetches employees based on optional section, sub_section and category filters.
    
    :param section: Optional section to filter by.
    :param sub_section: Optional sub-section to filter by.
    :param category: Optional category to filter by.
    :return: List of employee dictionaries.
    """
    query = Employee.query

    if section:
        query = query.filter(Employee.Section == section)
    if sub_section:
        query = query.filter(Employee.Sub_Section == sub_section)
    if category:
        query = query.filter(Employee.Category == category)
    
    employees = query.order_by(Employee.Emp_Id).all()
    
    result = []
    for emp in employees:
        daily_rate = round(float(emp.Gross_Salary or 0) / 30, 2)
        
        result.append({
            'Emp_Id': emp.Emp_Id,
            'Emp_Name': emp.Emp_Name,
            'Designation': emp.Designation,
            'Sub_Section': emp.Sub_Section,
            'Section': emp.Section,
            'Category': emp.Category,
            'Grade': emp.Grade,
            'Gross_Salary': float(emp.Gross_Salary or 0),
            'Daily_Rate': daily_rate
        })
    return result

def get_distinct_sections():
    """Returns a list of distinct sections."""
    results = db.session.query(distinct(Employee.Section)).filter(Employee.Section != None, Employee.Section != '').order_by(Employee.Section).all()
    return [r[0] for r in results]

def get_distinct_sub_sections(section=None):
    """Returns a list of distinct sub-sections, optionally filtered by section."""
    query = db.session.query(distinct(Employee.Sub_Section)).filter(Employee.Sub_Section != None, Employee.Sub_Section != '')
    if section:
        query = query.filter(Employee.Section == section)
    results = query.order_by(Employee.Sub_Section).all()
    return [r[0] for r in results]

def get_distinct_categories():
    """Returns a list of distinct categories."""
    results = db.session.query(distinct(Employee.Category)).filter(Employee.Category != None, Employee.Category != '').order_by(Employee.Category).all()
    return [r[0] for r in results]

def get_employee_count():
    """Returns the total number of employees."""
    return Employee.query.count()

def get_section_count():
    """Returns the count of distinct sub-sections."""
    return db.session.query(distinct(Employee.Sub_Section)).filter(Employee.Sub_Section != None, Employee.Sub_Section != '').count()
