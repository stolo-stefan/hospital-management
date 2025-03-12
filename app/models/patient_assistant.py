from app import db
from app.models.user import User
from app.models.patient import Patient

class PatientAssistant(db.Model):
    __tablename__ = 'patient_assistants'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    patient_id = db.Column(db.BigInteger,db.ForeignKey('patients.id', ondelete='CASCADE'),nullable=True)
    assistant_id = db.Column(db.BigInteger,db.ForeignKey('users.id', ondelete='CASCADE'),nullable=False)
    doctor_id = db.Column(db.BigInteger, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    patient = db.relationship('Patient', backref='patient_assistants', passive_deletes=True)
    assistant = db.relationship('User', foreign_keys=[assistant_id],backref='assisting_patients')
    supervising_doctor = db.relationship('User', foreign_keys=[doctor_id], backref='assigned_assistants')