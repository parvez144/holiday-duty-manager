import os
from flask import Flask, redirect, url_for, session, send_from_directory
from routes.main import main_bp
from routes.holiday_reports import holiday_reports_bp
from routes.api import api_bp
from routes.night_bill import night_bill_bp
from routes.auth import auth_bp
from routes.users import users_bp
from routes.security_payment import security_payment_bp
from routes.attendance_mgmt import attendance_mgmt_bp
from extensions import db, login_manager
from models.user import User
from system_config import system_info, user

app = Flask(__name__)
app.config.from_pyfile('config.py')

db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.context_processor
def inject_system_info():
    return dict(system=system_info, user=user)

@app.before_request
def make_session_permanent():
    session.permanent = True
    session.modified = True

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static', 'img'),
                               'logo.png', mimetype='image/png')

# Register blueprints
app.register_blueprint(main_bp)
app.register_blueprint(holiday_reports_bp)
app.register_blueprint(api_bp)
app.register_blueprint(night_bill_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(users_bp)
app.register_blueprint(security_payment_bp)
app.register_blueprint(attendance_mgmt_bp)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
