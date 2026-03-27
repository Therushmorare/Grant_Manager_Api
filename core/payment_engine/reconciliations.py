from database import db
from functions.user_logs import log_applicant_track
from functions.form_sanitizer import sanitize_input
from core.auth.account_checker import account_checker
from datetime import datetime
import uuid

def payment_reconciliation(officer_id, trench_id, visit_id, comments):
    try:
        if not account_checker(officer_id):
            return {'message': 'Officer does not exist'}, 404
        
        if not comments:
            return {'message': 'Please provide a reconciliation comment'}, 400
        
        trench = TrenchPlan.query.filter_by(trench_id=trench_id).first()
        if not trench:
            return {'message': 'Trench does not exist'}, 404
        
        inspection = Inspection.query.filter_by(visit_id=visit_id).first()
        if not inspection:
            return {'message': 'Inspection does not exist'}, 404
        
        journal = TransactionJournal.query.filter_by(trench_id=trench_id, status='PAID').first()
        if not journal:
            return {'message': 'No paid transaction found for this trench'}, 400

        existing_reversal = TransactionJournal.query.filter_by(
            trench_id=trench_id,
            status='REVERSAL'
        ).first()

        if existing_reversal:
            return {'message': 'This trench has already been reconciled'}, 409

        if trench.status != 'PAID':
            return {'message': 'Cannot reverse unpaid trench'}, 400
        
        if inspection.status != 'FAILED':
            return {'message': 'Reconciliation only allowed if inspection failed'}, 400


        trench.status = 'REVERSED'

        # Optional: update payment request too
        payment_request = PaymentRequest.query.filter_by(trench_id=trench_id).first()
        if payment_request:
            payment_request.status = 'REVERSED'

        reversal_entry = TransactionJournal(
            entry_id=str(uuid.uuid4()),
            trench_id=trench_id,
            request_id=journal.request_id,
            amount=journal.amount,
            status='REVERSAL',
            statement=sanitize_input(comments),
        )

        db.session.add(reversal_entry)
        db.session.commit()

        log_applicant_track(
            officer_id,
            'FINANCE_OFFICER',
            f'Reversed payment for trench {trench_id}'
        )

        return {
            'message': 'Reconciliation (reversal) processed successfully',
            'trench_status': 'REVERSED'
        }, 200

    except Exception as e:
        db.session.rollback()
        print(f'Reconciliation Error: {e}')
        return {'message': 'Something went wrong'}, 500