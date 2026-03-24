from models.contract import ContractAgreement, ContractSignature
from database import db
from functions.user_logs import log_applicant_track

"""
Delete Contract Agreement
"""
def delete_contract_agreement(officer_id, contract_id):
    try:
        contract = ContractAgreement.query.filter_by(
            contract_id=contract_id
        ).first()

        if not contract:
            return {'message': 'Contract agreement does not exist'}, 404

        if contract.contract_status != 'PENDING' or contract.is_signed:
            return {
                'message': 'Contract cannot be deleted once it has been signed or processed'
            }, 400

        # (Assuming only the creator/officer can delete)
        if contract.shared_by != officer_id:
            return {'message': 'Unauthorized to delete this contract'}, 403

        ContractSignature.query.filter_by(
            contract_id=contract_id
        ).delete(synchronize_session=False)

        db.session.delete(contract)

        db.session.commit()

        log_applicant_track(officer_id, 'FINANCE_OFFICER', f'Finance Officer:{officer_id} deleted contract:{contract_id}')

        return {'message': 'Contract was deleted successfully'}, 200

    except Exception as e:
        db.session.rollback()
        print(f'Contract agreement delete error: {e}')
        return {'message': 'Something went wrong'}, 500