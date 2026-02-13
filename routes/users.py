from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from models.user import User
from routes.auth import admin_required

users_bp = Blueprint('users', __name__)

@users_bp.route('/users')
@login_required
@admin_required
def list_users():
    users = User.query.all()
    return render_template('manage_users.html', users=users)

@users_bp.route('/users/add', methods=['POST'])
@login_required
@admin_required
def add_user():
    username = request.form.get('username')
    password = request.form.get('password')
    name = request.form.get('name')
    role = request.form.get('role')

    if User.query.filter_by(username=username).first():
        flash('Username already exists.', 'danger')
        return redirect(url_for('users.list_users'))

    new_user = User(username=username, name=name, role=role)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    
    flash(f'User {username} created successfully.', 'success')
    return redirect(url_for('users.list_users'))

@users_bp.route('/users/delete/<int:id>')
@login_required
@admin_required
def delete_user(id):
    user = User.query.get_or_404(id)
    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'danger')
        return redirect(url_for('users.list_users'))

    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully.', 'success')
    return redirect(url_for('users.list_users'))
