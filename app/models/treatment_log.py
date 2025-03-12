from app import db
from app.models.user import User
from app.models.patient import Patient
from app.models.treatment import Treatment

class TreatmentLog(db.Model):
    __tablename__ = 'treatment_logs'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    patient_id = db.Column(db.BigInteger, db.ForeignKey('patients.id', ondelete='CASCADE'), nullable=False)
    treatment_id = db.Column(db.BigInteger, db.ForeignKey('treatments.id', ondelete='CASCADE'), nullable=False)
    applied_by = db.Column(db.BigInteger, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    applied_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=True)
    notes = db.Column(db.Text, nullable=True)

    patient = db.relationship('Patient', backref='treatment_logs')
    treatment = db.relationship('Treatment', backref='treatment_logs')
    applying_assistant = db.relationship('User', foreign_keys=[applied_by], backref='treatment_logs')
