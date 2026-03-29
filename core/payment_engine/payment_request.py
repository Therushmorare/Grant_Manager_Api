from database import db
from core.auth.account_checker import account_checker
from functions.file_uploder import file_upload
import uuid
from datetime import datetime
from functions.user_logs import log_applicant_track
from models.trench import TrenchPlan
from models.applications import Applications
from models.payment_request import PaymentRequest

def payment_request(applicant_id, trench_id, progress_report):
    try:
        #Validate user
        if not account_checker(applicant_id):
            return {'message': 'User does not exist'}, 404
        
        #Get trench
        trench = TrenchPlan.query.filter_by(trench_id=trench_id).first()
        if not trench:
            return {'message': 'Trench plan does not exist'}, 404
        
        #Get application
        application = Applications.query.filter_by(application_id=trench.application_id).first()
        if not application:
            return {'message': 'Application does not exist'}, 404

        #Ownership check (VERY IMPORTANT)
        if application.applicant_id != applicant_id:
            return {'message': 'Unauthorized request'}, 403

        #Prevent duplicate requests
        existing_request = PaymentRequest.query.filter_by(trench_id=trench_id).first()
        if existing_request:
            return {'message': 'Payment already requested for this trench'}, 400

        request_id = str(uuid.uuid4())

        #Calculate funding
        funding = application.required_funding * (trench.percentage / 100)

        # FIRST TRENCH (AUTO PAYMENT)
        if trench.sequence == 1:

            if trench.status in ['PAID', 'APPROVED']:
                return {'message': 'First trench already processed'}, 400

            save_data = PaymentRequest(
                applicant_id=applicant_id,
                trench_id=trench_id,
                request_id=request_id,
                report=None,
                payment_request=funding,
                status='APPROVED',
                is_approved=True,
                approved_by=application.approved_by,
                comments='Request for payment was automatically approved on contract signage'
            )

            trench.status = 'APPROVED'

        #OTHER TRENCHES
        else:

            if trench.status != 'PENDING':
                return {'message': f'Trench cannot be requested. Current status: {trench.status}'}, 400

            if not progress_report:
                return {'message': 'Progress report is required'}, 400

            #Upload file
            file_url = file_upload(progress_report, trench_id)

            save_data = PaymentRequest(
                applicant_id=applicant_id,
                trench_id=trench_id,
                request_id=request_id,
                report=file_url,
                payment_request=funding,
                status='PENDING',
                is_approved=False,
                approved_by=None,
                comments=None
            )

            trench.status = 'REQUESTED'

        #Save everything
        db.session.add(save_data)
        db.session.commit()

        #Log
        log_applicant_track(
            applicant_id,
            'APPLICANT',
            f'Requested payment for trench {trench_id} (application: {trench.application_id})'
        )

        return {
            'message': 'Payment request processed successfully',
            'request_id': request_id,
            'amount': funding
        }, 200

    except Exception as e:
        db.session.rollback()
        print(f'Payment request error: {e}')
        return {'message': 'Something went wrong'}, 500