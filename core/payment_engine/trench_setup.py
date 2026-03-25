from core.auth.account_checker import account_checker
from functions.form_sanitizer import sanitize_input
from database import db
from functions.user_logs import log_applicant_track
import uuid

def trench_plan_maker(officer_id, application_id, trenches, percentage_per_trench):
    try:
        # Validate officer
        if not account_checker(officer_id):
            return {'message': 'Officer does not exist'}, 404
        
        # Validate application
        application = Applications.query.filter_by(application_id=application_id).first()
        if not application:
            return {'message': 'Application does not exist'}, 404
        
        if application.final_status != 'APPROVED':
            return {'message': 'Application has not been approved'}, 400
        
        # Validate funding
        funding = Funding.query.filter_by(application_id=application_id).first()
        if not funding:
            return {'message': 'Applicant funding does not exist'}, 404
        
        if funding.status != 'APPROVED':
            return {'message': 'Funding has not yet been approved'}, 400
        
        # Validate contract
        contract = ContractAgreement.query.filter_by(application_id=application_id).first()
        if not contract:
            return {'message': 'Contract does not exist'}, 404
        
        if contract.is_signed is not True:
            return {'message': 'Contract has not been signed'}, 400
        
        # Prevent duplicate trench plans
        existing = TrenchPlan.query.filter_by(application_id=application_id).first()
        if existing:
            return {'message': 'Trench plan already exists for this application'}, 400

        # Normalize inputs
        trenches = trenches or []
        percentage_per_trench = percentage_per_trench or []

        if len(trenches) != len(percentage_per_trench):
            return {'message': 'Mismatch between trenches and percentages'}, 400
        
        new_trenches = []
        total_percentage = 0

        for index, (trench, percentage) in enumerate(zip(trenches, percentage_per_trench), start=1):
            if not trench or not percentage:
                continue

            trench_clean = sanitize_input(trench).strip()

            try:
                percentage_value = float(percentage)
            except ValueError:
                return {'message': f'Invalid percentage value: {percentage}'}, 400

            if percentage_value <= 0:
                return {'message': 'Percentage must be greater than 0'}, 400

            total_percentage += percentage_value

            #First trench auto-approved
            status = 'APPROVED' if index == 1 else 'PENDING'

            new_trenches.append(
                TrenchPlan(
                    application_id=application_id,
                    officer_id=officer_id,
                    trench_id=str(uuid.uuid4()),
                    trench=trench_clean,
                    percentage=percentage_value,
                    sequence=index,
                    status=status
                )
            )

        # Ensure valid input
        if not new_trenches:
            return {'message': 'No valid inputs entered'}, 400

        # Ensure total = 100%
        if round(total_percentage, 2) != 100.00:
            return {'message': f'Total percentage must equal 100%. Current: {total_percentage}'}, 400

        # Save all at once
        db.session.add_all(new_trenches)
        db.session.commit()

        # Log activity
        log_applicant_track(
            officer_id,
            'FINANCE_OFFICER',
            f'Created a payment trench plan for application: {application_id}'
        )

        return {
            'message': 'Payment trench plan created successfully',
            'total_trenches': len(new_trenches),
            'first_trench_auto_approved': True
        }, 200

    except Exception as e:
        db.session.rollback()
        print(f'Trench Plan Error: {e}')
        return {'message': 'Something went wrong'}, 500