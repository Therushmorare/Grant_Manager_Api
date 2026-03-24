from database import db
from functions.user_logs import log_applicant_track
from datetime import datetime
"""
Funding Window approval workflows
"""

#Manager approvals
#statuses[PASSED, REJECTED]
VALID_MANAGER_STATUSES = ['PASSED', 'REJECTED']

def window_approval(manager_id, funding_window_id, status, notes=None):
    try:
        manager = Employee.query.filter_by(
            employee_id=manager_id,
            role='MANAGER'
        ).first()

        if not manager:
            return {'message': 'Manager not found'}, 404

        application = FundingWindow.query.filter_by(
            funding_window_id=funding_window_id
        ).first()

        if not application:
            return {'message': 'Application does not exist'}, 404

        # Validate status
        if status not in VALID_MANAGER_STATUSES:
            return {'message': 'Invalid status'}, 400

        # Enforce workflow
        if application.status != 'PENDING':
            return {
                'message': f'Cannot update application in {application.status} state'
            }, 400

        # Apply update
        application.status = status
        application.manager_id = manager_id
        application.manager_reviewed_at = datetime.utcnow()

        if notes:
            application.notes = notes

        db.session.commit()

        # Log
        log_applicant_track(
            manager_id,
            'MANAGER',
            f'Manager approved application:{funding_window_id} → {status}'
        )

        return {
            'message': 'Application status updated successfully',
            'status': status
        }, 200

    except Exception as e:
        db.session.rollback()
        print(f'Application status update error: {e}')

        return {
            'message': 'Something went wrong',
            'error': str(e)
        }, 500
    

#Admin Approval(Final)
#status[APPROVED, REJECTED]
VALID_ADMIN_STATUSES = ['APPROVED', 'REJECTED']

def final_window_approval(admin_id, funding_window_id, status, notes=None):
    try:
        admin = Admin.query.filter_by(admin_id=admin_id).first()

        if not admin:
            return {'message': 'Admin not found'}, 404

        application = FundingWindow.query.filter_by(
            funding_window_id=funding_window_id
        ).first()

        if not application:
            return {'message': 'Application does not exist'}, 404

        # Validate status
        if status not in VALID_ADMIN_STATUSES:
            return {'message': 'Invalid status'}, 400

        # Enforce workflow
        if application.status != 'PASSED':
            return {
                'message': f'Application must be PASSED before final approval (current: {application.status})'
            }, 400

        # Apply final decision
        application.final_status = status
        application.admin_id = admin_id

        if notes:
            application.final_notes = notes

        # update main status too
        if status == 'APPROVED':
            application.status = 'APPROVED'
        else:
            application.status = 'REJECTED'

        db.session.commit()

        # Log
        log_applicant_track(
            admin_id,
            'ADMIN',
            f'Final decision for application:{funding_window_id} → {status}'
        )

        return {
            'message': 'Final application status updated successfully',
            'final_status': status
        }, 200

    except Exception as e:
        db.session.rollback()
        print(f'Final approval error: {e}')

        return {
            'message': 'Something went wrong',
            'error': str(e)
        }, 500