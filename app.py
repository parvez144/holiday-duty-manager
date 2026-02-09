from flask import Flask, render_template
from routes.reports import reports_bp

app = Flask(__name__)

# Register blueprints
app.register_blueprint(reports_bp)

@app.route('/')
def index():
    return render_template('reports.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
