from core.auth.account_checker import account_checker
from functions.card_checker import validate_account_number, branch_checker
import uuid
from functions.form_sanitizer import sanitize_input
from functions.user_logs import log_applicant_track
from database import db

def banking_details(applicant_id, bank_name, account_holder, account_number, branch_code, account_type):
    try:
        # Check account exists
        if not account_checker(applicant_id):
            return {'message': 'Applicant does not exist'}, 404

        # Check required fields
        if any(x is None for x in [bank_name, account_holder, account_number, branch_code, account_type]):
            return {'message': 'Please enter complete details'}, 400

        # Validate account number
        acc_check = validate_account_number(account_number)
        if not acc_check.get("valid"):
            return {'message': acc_check.get("message", "Invalid account number")}, 400

        # Validate branch code
        branch_check = branch_checker(branch_code)
        if not branch_check.get("valid"):
            return {'message': branch_check.get("message", "Invalid branch code")}, 400

        # Save data
        bank_account_id = str(uuid.uuid4())

        save_data = BankAccounts(
            applicant_id=applicant_id,
            bank_account_id=bank_account_id,
            bank_name=sanitize_input(bank_name),
            account_holder=sanitize_input(account_holder),
            account_number=sanitize_input(account_number),
            branch_code=sanitize_input(branch_code),
            account_type=sanitize_input(account_type),
            verification_status='PENDING',
            is_verified=False,
            verified_by=None
        )

        db.session.add(save_data)
        db.session.commit()

        log_applicant_track(applicant_id, 'APPLICANT', 'Added banking details')

        return {'message': 'Banking details added successfully'}, 200

    except Exception as e:
        db.session.rollback()
        print(f'Banking details error: {e}')
        return {'message': 'Something went wrong'}, 500