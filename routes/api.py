from flask import Blueprint, jsonify, request
from flask_login import login_required
from services.employee_service import get_distinct_sections, get_distinct_sub_sections, get_distinct_categories

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
