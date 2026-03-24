from core.auth.account_checker import account_checker
from database import db
from functions.user_logs import log_applicant_track

#Approves application
VALID_MANAGER_RATINGS = [1, 2, 3, 4, 5]

def manager_review_engine(manager_id, applicant_id, application_id, rating, notes):
    try:
        #Validate manager role
        manager = Employee.query.filter_by(
            employee_id=manager_id,
            role='MANAGER'
        ).first()

        if not manager:
            return {'message': 'Manager not found'}, 404

        #Fetch application
        application = Applications.query.filter_by(
            applicant_id=applicant_id,
            application_id=application_id
        ).first()

        if not application:
            return {'message': 'Application does not exist'}, 404

        #Prevent re-review
        if application.application_status != 'PENDING':
            return {'message': 'Application already reviewed'}, 409

        #Validate rating
        if rating not in VALID_MANAGER_RATINGS:
            return {'message': 'Invalid rating'}, 400

        #Prevent duplicate rating
        existing_rating = ApplicationRating.query.filter_by(
            application_id=application_id,
            rated_by=manager_id
        ).first()

        if existing_rating:
            return {'message': 'You have already reviewed this application'}, 409

        #Update application
        application.application_status = 'REVIEWED'
        application.reviewed_by = manager_id

        #Save rating
        save_rating = ApplicationRating(
            applicant_id=applicant_id,
            application_id=application_id,
            rating=rating,
            notes=notes,
            rated_by=manager_id
        )

        db.session.add(save_rating)
        db.session.commit()

        #Log
        log_applicant_track(
            manager_id,
            'MANAGER',
            f'Reviewed application:{application_id} → status:REVIEWED'
        )

        return {'message': 'Application reviewed successfully'}, 200

    except Exception as e:
        db.session.rollback()
        print(f'Application review error: {e}')
        return {'message': 'Something went wrong'}, 500        


#Financial officer approves application for funding
VALID_FINANCE_STATUSES = ['APPROVED', 'REJECTED']

def finance_review_engine(officer_id, applicant_id, application_id, status, notes):
    try:
        #Validate finance officer
        officer = FinanceOfficer.query.filter_by(
            id=officer_id
        ).first()

        if not officer:
            return {'message': 'Finance officer not found'}, 404

        #Fetch application
        application = Applications.query.filter_by(
            applicant_id=applicant_id,
            application_id=application_id
        ).first()

        if not application:
            return {'message': 'Application does not exist'}, 404

        #Ensure manager reviewed first
        if application.application_status != 'REVIEWED':
            return {'message': 'Application not yet reviewed by manager'}, 400

        #Validate status
        if status not in VALID_FINANCE_STATUSES:
            return {'message': 'Invalid status'}, 400

        #Prevent double approval
        if application.final_status:
            return {'message': 'Application already finalized'}, 409

        #Update application
        application.final_status = status
        application.approved_by = officer_id

        #Only create funding if approved
        if status == 'APPROVED':
            existing_funding = Funding.query.filter_by(
                application_id=application_id
            ).first()

            if existing_funding:
                return {'message': 'Funding already exists'}, 409

            save_data = Funding(
                applicant_id=applicant_id,
                application_id=application_id,
                funding_window_id=application.funding_window_id,
                approved_funding=application.required_funding,
                status='APPROVED',
                notes=notes,
                approved_by=officer_id
            )

            db.session.add(save_data)

        db.session.commit()

        #Log
        log_applicant_track(
            officer_id,
            'FINANCE_OFFICER',
            f'Finalized application:{application_id} → {status}'
        )

        return {'message': 'Application final decision recorded'}, 200

    except Exception as e:
        db.session.rollback()
        print(f'Funding error: {e}')
        return {'message': 'Something went wrong'}, 500