from functions.form_sanitizer import sanitize_input
from database import db
from functions.registration_number_validator import validate_cipc
from functions.user_logs import log_applicant_track
import uuid
from core.auth.account_checker import account_checker
from models.applicant_profile import ApplicantProfile

def applicant_profile(
    applicant_id,
    company_legal_name,
    trading_name,
    registration_number,
    company_type,
    industry,
    seta_affiliation,
    registered_address,
    physical_address,
    city,
    province,
    postal_code,
    country):
    try:
        #Validate applicant first        
        if not account_checker(applicant_id):
            return {'message': 'Applicant does not exist'}, 404

        #Check if profile already exists
        existing_profile = ApplicantProfile.query.filter_by(
            applicant_id=applicant_id
        ).first()

        if existing_profile:
            return {'message': 'Profile already exists'}, 409

        #Validate required fields
        if not all([
            company_legal_name, trading_name, registration_number,
            company_type, industry, seta_affiliation,
            registered_address, physical_address,
            city, province, postal_code, country
        ]):
            return {'message': 'Please ensure all fields are filled'}, 400

        # Normalize + sanitize early
        rn_clean = sanitize_input(registration_number).upper().strip()

        #Validate registration number
        if not validate_cipc(rn_clean):
            return {'message': 'Please enter valid registration number'}, 400

        # Ensure registration number uniqueness
        profile_check = ApplicantProfile.query.filter_by(
            registration_number=rn_clean
        ).first()

        if profile_check:
            return {'message': 'Registration number already exists'}, 409

        #Sanitize all inputs
        cln = sanitize_input(company_legal_name)
        tn = sanitize_input(trading_name)
        ct = sanitize_input(company_type)
        i = sanitize_input(industry)
        seta = sanitize_input(seta_affiliation)
        ra = sanitize_input(registered_address)
        pa = sanitize_input(physical_address)
        c = sanitize_input(city).title()
        p = sanitize_input(province).title()
        pc = sanitize_input(postal_code)
        co = sanitize_input(country).title()

        #Generate profile ID
        profile_id = str(uuid.uuid4())

        #Save profile
        save_data = ApplicantProfile(
            profile_id=profile_id,
            applicant_id=applicant_id,
            legal_name=cln,
            trading_name=tn,
            registration_number=rn_clean,
            company_type=ct,
            industry=i,
            seta_affiliation=seta,
            registered_address=ra,
            physical_address=pa,
            city=c,
            province=p,
            postal_code=pc,
            country=co,
            verification_status='PENDING',
            is_verified=False,
            verified_by=None
        )

        db.session.add(save_data)
        db.session.commit()

        # Log activity
        log_applicant_track(
            applicant_id,
            'APPLICANT',
            f'Applicant:{applicant_id} created profile ID:{profile_id}'
        )

        return {
            'message': 'Profile created successfully',
            'profile_id': profile_id
        }, 201

    except Exception as e:
        db.session.rollback()
        print(f'Profile error: {e}')

        return {
            'message': 'Failed to create profile',
            'error': str(e)
        }, 500