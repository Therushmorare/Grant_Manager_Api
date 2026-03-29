from database import db
from core.auth.account_checker import account_checker
from functions.file_uploder import file_upload
import uuid
from functions.user_logs import log_applicant_track
from models.documents import ApplicantDocuments

VALID_DOC_TYPES = [
    'CIPC_Registration',
    'Tax_Clearance',
    'Bank_Confirmation_Letter',
    'Proof_of_Address',
    'Accreditation_Certificate'
]

def documents(applicant_id, doc_type, document):
    try:
        #Check applicant
        if not account_checker(applicant_id):
            return {'message': 'Applicant does not exist'}, 404

        #Validate inputs
        if not doc_type or not str(doc_type).strip():
            return {'message': 'Document type empty'}, 400

        if document is None:
            return {'message': 'Document is empty'}, 400

        doc_type = doc_type.strip()

        #Validate doc type
        if doc_type not in VALID_DOC_TYPES:
            return {'message': 'Invalid document type'}, 400

        #Prevent duplicate document types
        existing_doc = ApplicantDocuments.query.filter_by(
            applicant_id=applicant_id,
            type=doc_type
        ).first()

        if existing_doc:
            return {'message': f'{doc_type} already uploaded'}, 409

        #Generate ID
        doc_id = str(uuid.uuid4())

        #Upload file
        file_url = file_upload(document, doc_id)

        if not file_url:
            return {'message': 'File upload failed'}, 500

        #Save document
        save_doc = ApplicantDocuments(
            applicant_id=applicant_id,
            doc_id=doc_id,
            type=doc_type,
            document=file_url,
            verification_status='PENDING',
            is_verified=False,
            verified_by=None
        )

        db.session.add(save_doc)
        db.session.commit()

        #Log
        log_applicant_track(
            applicant_id,
            'APPLICANT',
            f'Uploaded document: {doc_type}'
        )

        return {'message': 'Document uploaded successfully'}, 200

    except Exception as e:
        db.session.rollback()
        print(f'Document upload error: {e}')
        return {'message': 'Something went wrong'}, 500