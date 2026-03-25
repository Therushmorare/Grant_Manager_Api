from database import db
from functions.user_logs import log_applicant_track
from core.auth.account_checker import account_checker
from functions.form_sanitizer import sanitize_input
from datetime import datetime

VALID_STATUS = ['APPROVED', 'REJECTED']

def review_payment_request(officer_id, request_id, status, comments):
    try:
        #Validate officer
        if not account_checker(officer_id):
            return {'message': 'Officer does not exist'}, 404
        
        #Get payment request
        payment_request = PaymentRequest.query.filter_by(request_id=request_id).first()
        if not payment_request:
            return {'message': 'Payment request does not exist'}, 404
        
        #Prevent re-review
        if payment_request.status != 'PENDING':
            return {'message': 'Payment request has already been reviewed'}, 409
        
        #Validate inputs
        if not status or status not in VALID_STATUS:
            return {'message': 'Select a valid status'}, 400
        
        if not comments:
            return {'message': 'Comments cannot be empty'}, 400

        #Get trench
        trench = TrenchPlan.query.filter_by(trench_id=payment_request.trench_id).first()
        if not trench:
            return {'message': 'Associated trench not found'}, 404

        #APPROVE
        if status == 'APPROVED':
            payment_request.status = 'APPROVED'
            payment_request.is_approved = True
            payment_request.approved_by = officer_id
            payment_request.comments = sanitize_input(comments)

            trench.status = 'APPROVED'

        #REJECT
        else:
            payment_request.status = 'REJECTED'
            payment_request.is_approved = False
            payment_request.approved_by = officer_id
            payment_request.comments = sanitize_input(comments)

            #reset trench so it can be requested again
            trench.status = 'PENDING'

        #Commit once
        db.session.commit()

        #Log
        log_applicant_track(
            officer_id,
            'FINANCE_OFFICER',
            f'Reviewed payment request {request_id} → {status}'
        )

        return {'message': f'Payment request {status.lower()} successfully'}, 200

    except Exception as e:
        db.session.rollback()
        print(f'Payment request review error: {e}')
        return {'message': 'Something went wrong'}, 500