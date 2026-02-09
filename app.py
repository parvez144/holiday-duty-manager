from flask import Flask, render_template
from routes import reports_bp
from extensions import db

app = Flask(__name__)
app.config.from_pyfile('config.py')

db.init_app(app)

# Register blueprints
app.register_blueprint(reports_bp)

@app.route('/')
def index():
    return render_template('dashboard.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
