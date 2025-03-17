from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import func
from sqlalchemy.sql import text
from app.models import User, Patient, Treatment, PatientTreatment, PatientAssistant
from app import db
from app.utils import get_current_user, check_json, get_user_by_id, check_role, update_user_fields

report_bp = Blueprint('reports_bp', __name__)

@report_bp.route('/doctors-patients', methods=['GET'])
@jwt_required()
def generate_doctor_patient_report():
    current_user = get_current_user()
    if current_user['role'] != 'General Manager':
        return jsonify({'error': 'Unauthorized'}), 401

    doctors = User.query.filter_by(role='Doctor').all()
    if not doctors:
        return jsonify({'error': 'No doctors found'}), 404

    from app.models.patient_assistant import PatientAssistant

    report_data = []
    total_patients = 0

    for doctor in doctors:
        patient_assignments = PatientAssistant.query.filter_by(doctor_id=doctor.id).all()
        patient_ids = {pa.patient_id for pa in patient_assignments}  # Get unique patient IDs

        patients = Patient.query.filter(Patient.id.in_(patient_ids)).all()
        total_patients += len(patients)

        report_data.append({
            'doctor_id': doctor.id,
            'doctor_name': doctor.name,
            'patients': [{'id': p.id, 'name': p.name} for p in patients]
        })

    total_doctors = len(doctors)
    avg_patients_per_doctor = total_patients / total_doctors if total_doctors > 0 else 0

    best_treatments = (
        db.session.query(Treatment.name, func.count(PatientTreatment.id).label("usage_count"))
        .join(PatientTreatment, Treatment.id == PatientTreatment.treatment_id)
        .group_by(Treatment.id)
        .order_by(func.count(PatientTreatment.id).desc())
        .limit(3)
        .all()
    )

    best_treatments_list = [{'name': t[0], 'times_prescribed': t[1]} for t in best_treatments]

    most_assigned_assistants = (
        db.session.query(User.name, func.count(PatientAssistant.patient_id).label("assigned_patients"))
        .join(PatientAssistant, User.id == PatientAssistant.assistant_id)
        .group_by(User.id)
        .order_by(func.count(PatientAssistant.patient_id).desc())
        .limit(3)
        .all()
    )

    top_assistants = [{'name': a[0], 'patients_assigned': a[1]} for a in most_assigned_assistants]

    applied_treatments = db.session.query(
        func.avg(text("TIMESTAMPDIFF(HOUR, patient_treatments.prescribed_at, patient_treatments.applied_at)"))
    ).filter(PatientTreatment.applied_at.isnot(None)).scalar()

    avg_time_to_apply = round(applied_treatments, 2) if applied_treatments else 0

    return jsonify({
        'report': report_data,
        'statistics': {
            'total_doctors': total_doctors,
            'total_patients': total_patients,
            'avg_patients_per_doctor': round(avg_patients_per_doctor, 2),
            'best_used_treatments': best_treatments_list,
            'most_assigned_assistants': top_assistants,
            'average_time_to_apply_treatment_hours': avg_time_to_apply
        }
    }), 200


@report_bp.route('/patient-treatments/<int:patient_id>', methods=['GET'])
@jwt_required()
def get_patient_treatments_report(patient_id):
    current_user = get_current_user()
    if current_user['role'] not in ['General Manager', 'Doctor']:
        return jsonify({'error': 'Unauthorized'}), 401

    patient = Patient.query.get(patient_id)
    if not patient:
        return jsonify({'error': 'Patient not found'}), 404

    if current_user['role'] == 'Doctor':
        supervising_relationship = PatientAssistant.query.filter_by(
            patient_id=patient_id,
            doctor_id=current_user['id']
        ).first()
        if not supervising_relationship:
            return jsonify({'error': 'This doctor does not supervise the patient'}), 403

    treatments = (
        db.session.query(
            Treatment.id,
            Treatment.name,
            Treatment.description,
            PatientTreatment.prescribed_by,
            PatientTreatment.applied_by,
            PatientTreatment.applied_at,
            PatientTreatment.status
        )
        .join(PatientTreatment, Treatment.id == PatientTreatment.treatment_id)
        .filter(PatientTreatment.patient_id == patient_id)
        .all()
    )

    treatment_list = []
    for treatment in treatments:
        treatment_list.append({
            'id': treatment.id,
            'name': treatment.name,
            'description': treatment.description,
            'prescribed_by': treatment.prescribed_by,
            'applied_by': treatment.applied_by,
            'applied_at': treatment.applied_at.strftime('%Y-%m-%d %H:%M:%S') if treatment.applied_at else None,
            'status': treatment.status
        })

    return jsonify({
        'patient_id': patient.id,
        'patient_name': patient.name,
        'treatments': treatment_list
    }), 200