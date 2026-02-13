from flask import Flask, redirect, url_for
from routes.main import main_bp
from routes.reports import reports_bp
from routes.auth import auth_bp
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

# Register blueprints
app.register_blueprint(main_bp)
app.register_blueprint(reports_bp)
app.register_blueprint(auth_bp)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
