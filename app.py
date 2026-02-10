from flask import Flask
from routes.main import main_bp
from routes.reports import reports_bp
from extensions import db
from system_config import system_info, user

app = Flask(__name__)
app.config.from_pyfile('config.py')

db.init_app(app)

@app.context_processor
def inject_system_info():
    return dict(system=system_info, user=user)

# Register blueprints
app.register_blueprint(main_bp)
app.register_blueprint(reports_bp)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
