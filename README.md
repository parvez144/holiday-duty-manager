# Holiday Duty Manager

A Flask-based web application designed for **Manel Fashion Limited** to manage employee attendance and automate holiday duty payment calculations.

## 🚀 Features

- **Attendance Tracking**: Integration with biometric data (BioTime) to track employee punches.
- **Holiday Duty Payments**: Automated calculation of daily basic salary for staff and overtime for workers.
- **Flexible Reporting**:
  - **Present Status Report**: Real-time view of raw punch times directly from the database.
  - **Payment Sheet**: Professional reports with rounding rules and overtime calculations.
  - **Exports**: Export reports as PDF (via WeasyPrint) and Excel (via openpyxl).
- **Security**: Configuration management using environment variables.
- **Production Ready**: Built-in support for Waitress WSGI server on Windows.

## 🛠️ Tech Stack

- **Backend**: Python, Flask
- **ORM**: SQLAlchemy (with multiple database binds)
- **Database**: MySQL (MFL Management & BioTime)
- **Production Server**: Waitress
- **Reports**: WeasyPrint, openpyxl, pandas

## 📦 Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/parvez144/holiday-duty-manager.git
   cd holiday-duty-manager
   ```

2. **Create a Virtual Environment**:

   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## ⚙️ Configuration

Copy the `.env.example` file to a new file named `.env` and fill in your actual credentials:

```bash
# Database Configuration
DB_HOST=your-db-host
DB_PORT=3306
DB_USER=your-db-user
DB_PASS=your-db-password

# Flask Security
SECRET_KEY=your-super-secret-key

# Developer & Admin Info
DEV_EMAIL=your-email@example.com
DEV_PHONE=+880 0000000000
ADMIN_NAME=Admin Name
ADMIN_PHONE=+880 0000000000
```

## 🏃 Running the Application

### Development Mode

```bash
python app.py
```

### Production Mode (Windows)

We recommend using the included batch file for easy startup:

- Simply double-click on `start_server.bat`
- Or run: `python serve.py`

## 📂 Project Structure

- `app.py`: Application entry point and configuration.
- `serve.py`: Production server script using Waitress.
- `config.py`: Environment-based configuration loader.
- `system_config.py`: Centralized system and developer metadata.
- `routes/`: Blueprint-based route definitions (reports, management, etc.).
- `services/`: Business logic for attendance and employee management.
- `models/`: Database models for employee and biometric data.
- `templates/`: HTML5 templates.
- `static/`: CSS, JS, and image assets.

## 📄 License & Copyright

- **Version**: 1.0.0
- **Developer**: Shahriar
- **Copyright**: © 2026 SPK. All rights reserved.
- **Client**: Manel Fashion Limited
