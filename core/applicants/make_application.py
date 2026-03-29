from functions.form_sanitizer import sanitize_input
from database import db
from core.auth.account_checker import account_checker
import uuid
from functions.file_uploder import file_upload
from functions.user_logs import log_applicant_track
from datetime import datetime
from models.applicant_profile import ApplicantProfile
from models.applications import Applications
from models.funding_window import FundingWindow

def make_application(
    applicant_id,
    funding_window_id,
    programme_title,
    programme_decription,
    category,
    type,
    required_funding,
    number_of_learners,
    start_date,
    end_date,
    proposal_doc
):
    try:
        #Check applicant
        if not account_checker(applicant_id):
            return {'message': 'Applicant does not exist'}, 404
        
        #check if profile is verified
        profile = ApplicantProfile.query.filter_by(applicant_id=applicant_id).first()
        if profile.verification_status == 'PENDING':
            return {'message': 'Your profile is not yet verified thus cannot file any applications until verification is complete.'}, 400

        #Check funding window
        funding_window = FundingWindow.query.filter_by(
            application_id=funding_window_id
        ).first()

        if not funding_window:
            return {'message': 'Funding window does not exist'}, 404

        #Prevent duplicate application
        existing = Applications.query.filter_by(
            funding_window_id=funding_window_id,
            applicant_id=applicant_id
        ).first()

        if existing:
            return {'message': 'You already applied for this funding window'}, 409

        #Validate inputs
        if not all([
            programme_title, programme_decription, category,
            type, required_funding, number_of_learners,
            start_date, end_date, proposal_doc
        ]):
            return {'message': 'Please fill out all inputs'}, 400

        #Ensure datetime
        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date)

        if isinstance(end_date, str):
            end_date = datetime.fromisoformat(end_date)

        if end_date <= start_date:
            return {'message': 'End date must be after start date'}, 400

        #Check funding window deadline
        if datetime.now() > funding_window.deadline:
            return {'message': 'Funding window is closed'}, 400

        #Upload proposal
        file_url = file_upload(proposal_doc, str(uuid.uuid4()))

        if not file_url:
            return {'message': 'File upload failed'}, 500

        #Duration in days
        duration_days = (end_date - start_date).days

        if duration_days <= 0:
            return {'message': 'Invalid project duration'}, 400

        #Cost per learner
        try:
            cost = float(required_funding) / float(number_of_learners)
        except:
            return {'message': 'Invalid funding or learner count'}, 400

        # Sanitize inputs
        save_data = Applications(
            application_id=str(uuid.uuid4()),
            funding_window_id=funding_window_id,
            applicant_id=applicant_id,
            programme_title=sanitize_input(programme_title),
            programme_decription=sanitize_input(programme_decription),
            category=sanitize_input(category),
            type=sanitize_input(type),
            required_funding=required_funding,
            number_of_learners=number_of_learners,
            cost_per_learner=cost,
            start_date=start_date,
            end_date=end_date,
            duration=duration_days,
            proposal_doc=file_url,
            application_status='PENDING',
            reviewed_by=None,
            final_status='PENDING',
            approved_by=None
        )

        db.session.add(save_data)
        db.session.commit()

        #Log
        log_applicant_track(
            applicant_id,
            'APPLICANT',
            f'Applied for funding window:{funding_window_id}'
        )

        return {
            'message': 'Applied for funding window successfully'
        }, 201

    except Exception as e:
        db.session.rollback()
        print(f'Application Error: {e}')
        return {'message': 'Something went wrong'}, 500