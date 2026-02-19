from models.employee import Employee
from models.section import Section
from models.sub_section import SubSection
from extensions import db
from sqlalchemy import distinct
from sqlalchemy.orm import joinedload

def get_employees(section=None, sub_section=None, category=None):
    """
    Fetches employees based on optional section, sub_section and category filters.
    """
    query = Employee.query
    
    # Efficiently fetch relationships
    query = query.options(
        joinedload(Employee.designation_rel),
        joinedload(Employee.sub_section_rel).joinedload(SubSection.section_rel)
    )

    if section:
        # Filter by Parent Section Name
        query = query.join(Employee.sub_section_rel).join(SubSection.section_rel).filter(Section.name == section)
    if sub_section:
        # Filter by SubSection Name
        query = query.join(Employee.sub_section_rel).filter(SubSection.name == sub_section)
    if category:
        query = query.filter(Employee.Category == category)
    
    employees = query.order_by(Employee.Emp_Id).all()
    
    result = []
    for emp in employees:
        gross_val = float(emp.Gross_Salary or 0)
        daily_rate = round(gross_val / 30, 2)
        
        # Merge related data
        desig_info = emp.designation_rel.designation if emp.designation_rel else ""
        grade_info = emp.designation_rel.grade if emp.designation_rel else emp.Grade
        
        sec_info = ""
        sub_sec_info = ""
        if emp.sub_section_rel:
            sub_sec_info = emp.sub_section_rel.name
            if emp.sub_section_rel.section_rel:
                sec_info = emp.sub_section_rel.section_rel.name

        result.append({
            'Emp_Id': emp.Emp_Id,
            'Emp_Name': emp.Emp_Name,
            'Designation': desig_info,
            'Sub_Section': sub_sec_info,
            'Section': sec_info,
            'Category': emp.Category,
            'Grade': grade_info,
            'Gross_Salary': gross_val,
            'Daily_Rate': daily_rate,
            'designation_obj': emp.designation_rel
        })
    return result

def get_distinct_sections():
    """Returns a list of distinct sections from the new Section table."""
    results = Section.query.order_by(Section.name).all()
    return [s.name for s in results]

def get_distinct_sub_sections(section=None):
    """Returns a list of distinct sub-sections, optionally filtered by section name."""
    query = SubSection.query
    if section:
        query = query.join(SubSection.section_rel).filter(Section.name == section)
    results = query.order_by(SubSection.name).all()
    return [s.name for s in results]

def get_distinct_categories():
    """Returns a list of distinct categories from employee table."""
    results = db.session.query(distinct(Employee.Category)).filter(Employee.Category != None, Employee.Category != '').order_by(Employee.Category).all()
    return [r[0] for r in results]

def get_employee_count():
    """Returns the total number of employees."""
    return Employee.query.count()

def get_section_count():
    """Returns the count of distinct sub-sections."""
    return SubSection.query.count()
