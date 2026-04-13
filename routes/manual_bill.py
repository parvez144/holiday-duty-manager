from flask import Blueprint, render_template, request, jsonify, redirect, url_for, send_file
from flask_login import login_required, current_user
from extensions import db
from models.manual_bill import ManualBill, ManualBillItem
from datetime import datetime
import io
import json
from weasyprint import HTML

manual_bill_bp = Blueprint('manual_bill', __name__)

@manual_bill_bp.route('/manual_bill')
@login_required
def list_bills():
    bills = ManualBill.query.order_by(ManualBill.bill_date.desc(), ManualBill.id.desc()).all()
    return render_template('manual_bill_list.html', bills=bills)

@manual_bill_bp.route('/manual_bill/create')
@login_required
def create_bill():
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('manual_bill_form.html', today=today, bill=None)

@manual_bill_bp.route('/manual_bill/save', methods=['POST'])
@login_required
def save_bill():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
        
    bill_id = data.get('id')
    title = data.get('title')
    bill_date_str = data.get('bill_date')
    prepared_by = data.get('prepared_by') or current_user.name
    items = data.get('items', [])
    
    try:
        bill_date = datetime.strptime(bill_date_str, '%Y-%m-%d').date()
    except Exception:
        bill_date = datetime.now().date()
        
    total_amount = sum(float(item.get('amount', 0)) for item in items)
    
    if bill_id:
        bill = ManualBill.query.get(bill_id)
        if not bill:
            return jsonify({'error': 'Bill not found'}), 404
        bill.title = title
        bill.bill_date = bill_date
        bill.prepared_by = prepared_by
        bill.total_amount = total_amount
        
        # Replace items
        ManualBillItem.query.filter_by(bill_id=bill.id).delete()
    else:
        bill = ManualBill(title=title, bill_date=bill_date, prepared_by=prepared_by, total_amount=total_amount)
        db.session.add(bill)
        
    db.session.flush() # To get bill.id
    
    for item in items:
        new_item = ManualBillItem(
            bill_id=bill.id,
            emp_id=item.get('emp_id'),
            name=item.get('name'),
            designation=item.get('designation'),
            description=item.get('description'),
            qty=float(item.get('qty', 1)),
            rate=float(item.get('rate', 0)),
            amount=float(item.get('amount', 0))
        )
        db.session.add(new_item)
        
    db.session.commit()
    return jsonify({'success': True, 'id': bill.id})

@manual_bill_bp.route('/manual_bill/edit/<int:bill_id>')
@login_required
def edit_bill(bill_id):
    bill = ManualBill.query.get_or_404(bill_id)
    items = ManualBillItem.query.filter_by(bill_id=bill.id).all()
    
    bill_data = {
        'id': bill.id,
        'title': bill.title,
        'bill_date': bill.bill_date.strftime('%Y-%m-%d'),
        'prepared_by': bill.prepared_by,
        'items': [{
            'emp_id': item.emp_id or '',
            'name': item.name or '',
            'designation': item.designation or '',
            'description': item.description or '',
            'qty': float(item.qty),
            'rate': float(item.rate),
            'amount': float(item.amount)
        } for item in items]
    }
    
    return render_template('manual_bill_form.html', bill=bill, bill_data_json=json.dumps(bill_data))

@manual_bill_bp.route('/manual_bill/delete/<int:bill_id>', methods=['POST'])
@login_required
def delete_bill(bill_id):
    bill = ManualBill.query.get_or_404(bill_id)
    db.session.delete(bill)
    db.session.commit()
    return jsonify({'success': True})

@manual_bill_bp.route('/manual_bill/pdf/<int:bill_id>')
@login_required
def pdf_bill(bill_id):
    bill = ManualBill.query.get_or_404(bill_id)
    items = ManualBillItem.query.filter_by(bill_id=bill.id).all()
    
    html_content = render_template(
        'manual_bill_pdf.html',
        bill=bill,
        items=items,
        datetime=datetime
    )

    pdf_buffer = io.BytesIO()
    HTML(string=html_content, base_url=request.url_root).write_pdf(pdf_buffer)
    pdf_buffer.seek(0)
    return send_file(pdf_buffer, as_attachment=False, mimetype='application/pdf')
