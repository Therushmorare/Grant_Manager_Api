from core.auth.account_checker import account_checker
from database import db
from functions.user_logs import log_applicant_track

def delete_user(admin_id, user_id):
    try:
        if not account_checker(admin_id):
            return {'message': 'Admin user does not exist'}, 404

        user = (
            Applicant.query.filter_by(id=user_id).first() or
            ADMIN.query.filter_by(id=user_id).first() or
            Employee.query.filter_by(id=user_id).first() or
            FinanceOfficer.query.filter_by(id=user_id).first() or 
            Monitor.query.filter_by(id=user_id).first()
        )

        if not user:
            return {'message': 'User does not exist'}, 404

        if hasattr(user, 'role') and user.role == 'SUPER_ADMIN':
            return {'message': 'Cannot delete SUPER_ADMIN account'}, 403

        if user.status == 'DELETED':
            return {'message': 'User already deleted'}, 409

        user.status = 'DELETED'
        user.is_active = False

        db.session.commit()

        log_applicant_track(
            admin_id,
            'ADMIN',
            f'Admin deleted user {user_id}'
        )

        return {
            'message': 'User deleted successfully',
            'user_id': user_id,
            'status': 'DELETED'
        }, 200

    except Exception as e:
        db.session.rollback()
        print(f'Delete user error: {e}')
        return {'message': 'Something went wrong'}, 500