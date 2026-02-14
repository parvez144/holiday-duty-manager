from app import app
from models.employee import Employee
with app.app_context():
    emps = Employee.query.filter(Employee.Sub_Section.ilike('%security%')).all()
    for e in emps:
        print(f"ID: {e.Emp_Id}, Name: {e.Emp_Name}, Section: {e.Section}, Sub-Section: {e.Sub_Section}")
