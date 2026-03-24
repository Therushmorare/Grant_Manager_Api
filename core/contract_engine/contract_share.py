from core.auth.account_checker import account_checker
from functions.file_uploder import file_upload
from functions.user_logs import log_applicant_track
from models.contract import ContractAgreement

"""
Share contract
"""
def share_contract(officer_id, applicant_id, application_id, contract_document):
    try:

        if not account_checker(officer_id):
            return {'message': 'Officer does not exist'}, 404

        application = Applications.query.filter_by(
            application_id=application_id
        ).first()

        if not application:
            return {'message': 'Application does not exist'}, 404

        if application.applicant_id != applicant_id:
            return {'message': 'Application does not belong to this applicant'}, 403

        if application.final_status != 'APPROVED':
            return {'message': 'Application has not yet been approved'}, 400

        funding = Funding.query.filter_by(
            application_id=application_id
        ).first()

        if not funding:
            return {'message': 'Funding Eligibility does not exist'}, 404

        if funding.status != 'APPROVED':
            return {'message': 'Funding has not yet been approved'}, 400

        if not contract_document:
            return {'message': 'No contract document provided'}, 400

        contract_id = str(uuid.uuid4())

        file_url = file_upload(contract_document, contract_id)

        if not file_url:
            return {'message': 'File upload failed'}, 500

        contract = ContractAgreement(
            contract_id=contract_id,
            applicant_id=applicant_id,
            application_id=application_id,
            contract=file_url,
            shared_by=officer_id,
            contractor_signature=None,
            applicant_signature=None,
            contract_status='PENDING_SIGNING',
            is_signed=False
        )

        db.session.add(contract)
        db.session.commit()

        log_applicant_track(
            officer_id,
            'FINANCE_OFFICER',
            f'Contract issued to applicant {applicant_id} for application {application_id}'
        )

        return {'message': 'Contract shared successfully'}, 200

    except Exception as e:
        db.session.rollback()
        print(f'Contract Agreement Error: {e}')
        return {'message': 'Something went wrong'}, 500