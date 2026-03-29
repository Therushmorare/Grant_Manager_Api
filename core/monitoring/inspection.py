from database import db
from core.auth.account_checker import account_checker
from functions.file_uploder import file_upload
from functions.user_logs import log_applicant_track
import uuid
from models.inspection import Inspection
from models.visit import SiteVisit

VISIT_STATUS = ['PASSES', 'FAILED']
def site_inspection(monitor_id, visit_id, status, comments, evidence_docs):
    try:
        if not account_checker(monitor_id):
            return {'message': 'Monitorer does not exist'}, 404

        visit = SiteVisit.query.filter_by(visit_id=visit_id).first()
        if not visit:
            return {'message': 'Site visit schedule does not exist'}, 404

        if any(x is None for x in [status, comments, evidence_docs]):
            return {'message': 'Please fill out all inputs'}, 400

        if status not in VISIT_STATUS:
            return {'message': 'Select a valid status'}, 400

        evidence_docs = evidence_docs or []

        visit.status = 'COMPLETE'

        for evidence_file in evidence_docs:
            if not evidence_file:
                continue

            file_url = file_upload(evidence_file, visit_id)

            inspection = Inspection(
                application_id=visit.application_id,
                visit_id=visit_id,
                monitor_id=monitor_id,
                status=status,
                comments=comments,
                file_id=str(uuid.uuid4()),
                file=file_url
            )

            db.session.add(inspection)

        db.session.commit()

        log_applicant_track(
            monitor_id,
            'MONITORER',
            f'Added Site Inspection'
        )

        return {'message': 'Site inspected successfully'}, 200

    except Exception as e:
        db.session.rollback()
        print(f'Inspection error: {e}')
        return {'message': 'Something went wrong'}, 500