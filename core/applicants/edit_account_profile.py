from functions.form_sanitizer import sanitize_input
from database import db
from functions.registration_number_validator import validate_cipc
from functions.user_logs import log_applicant_track
from datetime import datetime

def edit_applicant_profile(
    applicant_id,
    company_legal_name=None,
    trading_name=None,
    registration_number=None,
    company_type=None,
    industry=None,
    seta_affiliation=None,
    registered_address=None,
    physical_address=None,
    city=None,
    province=None,
    postal_code=None,
    country=None
):
    try:
        #Validate applicant
        applicant = Applicant.query.filter_by(id=applicant_id).first()
        if not applicant:
            return {'message': 'Applicant does not exist'}, 404

        #Fetch profile
        profile = ApplicantProfile.query.filter_by(
            applicant_id=applicant_id
        ).first()

        if not profile:
            return {'message': 'Profile does not exist'}, 404

        #Lock critical fields if verified
        if profile.verification_status:
            if registration_number:
                return {
                    'message': 'Cannot update registration number after verification'
                }, 403

            if company_legal_name:
                return {
                    'message': 'Cannot update legal name after verification'
                }, 403

        #Update fields (partial updates)

        if company_legal_name:
            profile.legal_name = sanitize_input(company_legal_name)

        if trading_name:
            profile.trading_name = sanitize_input(trading_name)

        if registration_number:
            rn_clean = sanitize_input(registration_number).upper().strip()

            if not validate_cipc(rn_clean):
                return {'message': 'Invalid registration number'}, 400

            #Ensure uniqueness
            existing = ApplicantProfile.query.filter(
                ApplicantProfile.registration_number == rn_clean,
                ApplicantProfile.applicant_id != applicant_id
            ).first()

            if existing:
                return {'message': 'Registration number already exists'}, 409

            profile.registration_number = rn_clean

        if company_type:
            profile.company_type = sanitize_input(company_type)

        if industry:
            profile.industry = sanitize_input(industry)

        if seta_affiliation:
            profile.seta_affiliation = sanitize_input(seta_affiliation)

        if registered_address:
            profile.registered_address = sanitize_input(registered_address)

        if physical_address:
            profile.physical_address = sanitize_input(physical_address)

        if city:
            profile.city = sanitize_input(city).title()

        if province:
            profile.province = sanitize_input(province).title()

        if postal_code:
            profile.postal_code = sanitize_input(postal_code)

        if country:
            profile.country = sanitize_input(country).title()

        #Track update time (add column if you don’t have it)
        if hasattr(profile, "updated_at"):
            profile.updated_at = datetime.utcnow()

        db.session.commit()

        #Log activity
        log_applicant_track(
            applicant_id,
            'APPLICANT',
            f'Applicant:{applicant_id} updated profile'
        )

        return {
            'message': 'Profile updated successfully'
        }, 200

    except Exception as e:
        db.session.rollback()
        print(f'Edit profile error: {e}')

        return {
            'message': 'Failed to update profile',
            'error': str(e)
        }, 500