from extensions import db

class SubSection(db.Model):
    __tablename__ = 'sub_sections'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('sections.id'), nullable=False)
    
    section_rel = db.relationship('Section', backref='sub_sections')

    def __repr__(self):
        return f'<SubSection {self.name}>'
