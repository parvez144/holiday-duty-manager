from extensions import db

class Employee(db.Model):
    __tablename__ = 'employees'

    Emp_Id = db.Column(db.Integer, primary_key=True)
    Emp_Name = db.Column(db.String(255), nullable=False)
    designation_id = db.Column(db.Integer, db.ForeignKey('designations.id'), nullable=True)
    Sub_Section = db.Column(db.String(100))
    Section = db.Column(db.String(100))
    Category = db.Column(db.String(50))
    Grade = db.Column(db.String(50))
    Gross_Salary = db.Column(db.Numeric(15, 2))
    
    designation_rel = db.relationship('Designation', backref='employees')
    
    # We can add other columns if needed, but these are the ones used in reports.
    
    def __repr__(self):
        return f'<Employee {self.Emp_Name}>'
