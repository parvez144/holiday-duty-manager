from flask import Blueprint, jsonify, request
from flask_login import login_required
from services.employee_service import get_distinct_sections, get_distinct_sub_sections, get_distinct_categories
from models.employee import Employee

api_bp = Blueprint('api', __name__, url_prefix='/api/reports')

@api_bp.route('/sections')
@login_required
def api_sections():
    """Return distinct section list from employees."""
    return jsonify(get_distinct_sections())

@api_bp.route('/sub_sections')
@login_required
def api_sub_sections():
    """Return distinct sub_section list from employees, optionally filtered by section."""
    section = request.args.get('section')
    return jsonify(get_distinct_sub_sections(section=section))

@api_bp.route('/categories')
@login_required
def api_categories():
    """Return distinct category list from employees."""
    return jsonify(get_distinct_categories())

@api_bp.route('/employees/search')
@login_required
def api_search_employees():
    """Return employees matching a query on Emp_Id or Emp_Name."""
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify([])
    
    if query.isdigit():
        # Search by exact ID or partial Name
        employees = Employee.query.filter(
            (Employee.Emp_Id == int(query)) | (Employee.Emp_Name.like(f'%{query}%'))
        ).limit(10).all()
    else:
        # Search by name only
        employees = Employee.query.filter(
            Employee.Emp_Name.like(f'%{query}%')
        ).limit(10).all()
    
    results = []
    for emp in employees:
        designation = emp.designation_rel.designation if emp.designation_rel else ""
        results.append({
            'id': emp.Emp_Id,
            'name': emp.Emp_Name,
            'designation': designation
        })
    return jsonify(results)
