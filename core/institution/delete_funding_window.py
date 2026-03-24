from database import db
from functions.user_logs import log_applicant_track

"""
Delete funding window
"""
def delete_funding_window(user_id, funding_window_id):
    try:
        # Validate user
        user = Employee.query.filter_by(employee_id=user_id).first()

        if not user:
            return {'message': 'User does not exist'}, 404
        
        if user.role != 'EMPLOYEE':
            return {'message': 'You do not have permission to delete this'}, 403

        # Get funding window
        application = FundingWindow.query.filter_by(
            funding_window_id=funding_window_id
        ).first()

        if not application:
            return {'message': 'Application does not exist'}, 404

        # Ownership check
        if application.poster_id != user_id:
            return {'message': 'Unauthorized to delete this funding window'}, 403

        # Prevent deletion if applicants exist
        if application.applicant_count and application.applicant_count > 0:
            return {
                'message': 'Cannot delete funding window with active applicants'
            }, 403

        # Delete related data 
        Requirements.query.filter_by(funding_window_id=funding_window_id).delete()
        Categories.query.filter_by(funding_window_id=funding_window_id).delete()

        # Delete main record
        db.session.delete(application)

        db.session.commit()

        # Log action
        log_applicant_track(
            user_id,
            'EMPLOYEE',
            f'Employee:{user_id} deleted funding window ID:{funding_window_id}'
        )

        return {'message': 'Funding window deleted successfully'}, 200

    except Exception as e:
        db.session.rollback()
        print(f'Delete funding window error: {e}')

        return {
            'message': 'Failed to delete funding window',
            'error': str(e)
        }, 500