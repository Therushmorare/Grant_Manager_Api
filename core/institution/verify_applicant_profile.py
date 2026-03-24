from functions.user_logs import log_applicant_track
from database import db
from datetime import datetime

VALID_MANAGER_STATUSES = ['VERIFIED', 'BLOCKED']

def verify_applicant(manager_id, applicant_id, profile_id, status, notes=None):
    try:
        #Validate manager
        manager = Employee.query.filter_by(
            employee_id=manager_id,
            role='MANAGER'
        ).first()

        if not manager:
            return {'message': 'Manager not found'}, 404

        #Fetch profile
        profile = ApplicantProfile.query.filter_by(
            applicant_id=applicant_id,
            profile_id=profile_id
        ).first()

        if not profile:
            return {'message': 'Profile does not exist'}, 404

        #Fetch dependencies
        contacts = ContactPersons.query.filter_by(applicant_id=applicant_id).all()
        banking = BankAccounts.query.filter_by(applicant_id=applicant_id).first()
        docs = ApplicantDocuments.query.filter_by(applicant_id=applicant_id).all()

        #Ensure completeness
        if not contacts:
            return {'message': 'Contact details missing'}, 400

        if not banking:
            return {'message': 'Banking details missing'}, 400

        if not docs:
            return {'message': 'Compliance documents missing'}, 400

        #Validate status
        if status not in VALID_MANAGER_STATUSES:
            return {'message': 'Invalid status'}, 400

        #Prevent double review
        if profile.verification_status != 'PENDING':
            return {
                'message': f'Profile already reviewed ({profile.verification_status})'
            }, 409

        #Apply decision to profile
        profile.verification_status = status
        profile.verified_by = manager_id
        profile.is_verified = (status == 'VERIFIED')
        profile.verified_at = datetime.utcnow()

        if notes:
            profile.notes = notes

        #Apply decision to banking
        if banking.verification_status == 'PENDING':
            banking.verification_status = status
            banking.verified_by = manager_id

        #apply decision to ALL documents
        for doc in docs:
            if doc.verification_status == 'PENDING':
                doc.verification_status = status
                doc.verified_by = manager_id

        db.session.commit()

        #Log
        log_applicant_track(
            manager_id,
            'MANAGER',
            f'Verified applicant:{applicant_id} profile:{profile_id} → {status}'
        )

        return {
            'message': 'Applicant verification completed',
            'status': status
        }, 200

    except Exception as e:
        db.session.rollback()
        print(f'Profile status update error: {e}')

        return {
            'message': 'Something went wrong',
            'error': str(e)
        }, 500