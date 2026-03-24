from database import db
from models.contract import ContractAgreement, ContractSignature
from functions.user_logs import log_applicant_track
from functions.form_sanitizer import sanitize_input

def applicant_sign_contract(contract_id, signer_name, signer_email, signature_data):
    """
    Applicant signs a contract.
    Updates contract status to SIGNED after signing.
    """
    contract = ContractAgreement.query.filter_by(contract_id=contract_id).first()
    if not contract:
        return {'message': 'Contract not found'}, 404

    if contract.is_signed:
        return {'message': 'Contract already signed'}, 400

    # Save signature
    signature = ContractSignature(
        contract_id=contract.contract_id,
        signer_name=sanitize_input(signer_name),
        signer_email=sanitize_input(signer_email),
        signature_data=signature_data
    )
    db.session.add(signature)
    db.session.commit()

    # Log the action
    log_applicant_track(
        contract.applicant_id,
        "APPLICANT",
        f"Applicant signed contract {contract_id}"
    )

    return {'message': 'Contract signed successfully'}, 200


def officer_sign_contract(contract_id, officer_id, signature_data):
    contract = ContractAgreement.query.filter_by(contract_id=contract_id).first()
    if not contract:
        return {'message': 'Contract not found'}, 404
    
    officer = FinanceOfficer.query.filter_by(id=officer_id).first()
    if not officer:
        return {'message': 'Officer does not exist'}, 404

    # Save officer signature
    signature = ContractSignature(
        contract_id=contract.contract_id,
        signer_name=officer.first_name+officer.last_name,
        signer_email=officer.email,
        signature_data=signature_data
    )
    db.session.add(signature)

    # Only mark fully signed if applicant already signed
    applicant_signed = ContractSignature.query.filter_by(
        contract_id=contract.contract_id
    ).filter(ContractSignature.signer_email.notlike('officer%')).count() > 0

    if applicant_signed:
        contract.is_signed = True
        contract.contract_status = "SIGNED"

    db.session.commit()

    # Log the action
    log_applicant_track(
        officer_id,
        "FINANCE_OFFICER",
        f"Finance Officer signed contract {contract_id}"
    )

    return {'message': 'Officer signature saved'}, 200