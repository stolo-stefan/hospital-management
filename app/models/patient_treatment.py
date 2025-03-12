from app import db
from app.models.user import User
from app.models.patient import Patient
from app.models.treatment import Treatment

class PatientTreatment(db.Model):
    __tablename__ = 'patient_treatments'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    patient_id = db.Column(db.BigInteger, db.ForeignKey('patients.id', ondelete='CASCADE'), nullable=False)
    treatment_id = db.Column(db.BigInteger, db.ForeignKey('treatments.id', ondelete='CASCADE'), nullable=False)
    prescribed_by = db.Column(db.BigInteger, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    applied_by = db.Column(db.BigInteger, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    prescribed_at = db.Column(db.DateTime, nullable=True)
    applied_at = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.Enum('prescribed', 'applied', name='status_enum'), default='prescribed')

    patient = db.relationship('Patient', backref=db.backref('patient_treatments', passive_deletes=True))
    treatment = db.relationship('Treatment', backref='patient_treatments')
    prescribing_doctor = db.relationship('User', foreign_keys=[prescribed_by], backref='prescribed_treatments')
    applying_assistant = db.relationship('User', foreign_keys=[applied_by], backref='applied_treatments')
