from app import db

class Patient(db.Model):
    __tablename__ = 'patients'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
