from database import db
from functions.user_logs import log_applicant_track
from core.auth.account_checker import account_checker
from datetime import datetime
import uuid
from models.trench import TrenchPlan
from models.payment_request import PaymentRequest
from models.journal import TransactionJournal

def log_payments(officer_id, trench_id):
    try:
        if not account_checker(officer_id):
            return {'message': 'Officer does not exist'}, 404

        trench = TrenchPlan.query.filter_by(trench_id=trench_id).first()
        if not trench:
            return {'message': 'Trench plan does not exist'}, 404

        request = PaymentRequest.query.filter_by(trench_id=trench_id).first()
        if not request:
            return {'message': 'Payment request does not exist'}, 404

        if request.status == 'PAID' or trench.status == 'PAID':
            return {'message': 'This trench has already been marked as paid'}, 409

        if request.status != 'APPROVED':
            return {'message': 'Payment request must be approved before payment'}, 400

        if trench.status != 'APPROVED':
            return {'message': 'Trench must be approved before payment'}, 400

        request.status = 'PAID'
        trench.status = 'PAID'

        entry_id = str(uuid.uuid4())

        transaction = TransactionJournal(
            entry_id=entry_id,
            trench_id=trench_id,
            request_id=request.request_id,
            amount=request.amount,
            status='PAID',
            statement='Funds successfully disbursed',
        )

        db.session.add(transaction)

        db.session.commit()


        log_applicant_track(
            officer_id,
            'FINANCE_OFFICER',
            f'Payment of {request.amount} marked as PAID for trench {trench_id}'
        )

        return {
            'message': 'Payment successfully processed',
            'data': {
                'entry_id': entry_id,
                'trench_id': trench_id,
                'amount': request.amount,
                'status': 'PAID'
            }
        }, 200

    except Exception as e:
        db.session.rollback()
        print(f'Payment logger error: {e}')
        return {'message': 'Something went wrong'}, 500