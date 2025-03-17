import json
from app import db, create_app
from app.models import User, Patient, Treatment, PatientTreatment, PatientAssistant
from werkzeug.security import generate_password_hash

app = create_app()

def load_fixtures():
    with app.app_context():
        with open("fixtures/sample_data_base_schema.json") as f:
            data = json.load(f)
            for item in data:
                if item["model"] == "User":
                    user = User(
                        name=item["fields"]["name"],
                        role=item["fields"]["role"],
                        password_hash=generate_password_hash(item["fields"]["password"])
                    )
                    db.session.add(user)
                elif item["model"] == "Patient":
                    patient = Patient(name=item["fields"]["name"])
                    db.session.add(patient)
                elif item["model"] == "Treatment":
                    treatment = Treatment(
                        name=item["fields"]["name"],
                        description=item["fields"]["description"]
                    )
                    db.session.add(treatment)
                elif item["model"] == "PatientTreatment":
                    patient_treatment = PatientTreatment(
                        patient_id=item["fields"]["patient_id"],
                        treatment_id=item["fields"]["treatment_id"],
                        prescribed_by=item["fields"]["prescribed_by"],
                        status=item["fields"]["status"]
                    )
                    db.session.add(patient_treatment)
                elif item["model"] == "PatientAssistant":
                    patient_assistant = PatientAssistant(
                        patient_id=item["fields"]["patient_id"],
                        assistant_id=item["fields"]["assistant_id"],
                        doctor_id=item["fields"]["doctor_id"]
                    )
                    db.session.add(patient_assistant)
            
            db.session.commit()
            print("Preset data loaded successfully.")

if __name__ == "__main__":
    load_fixtures()