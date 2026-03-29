from core.auth.account_checker import account_checker
from database import db
from functions.user_logs import log_applicant_track
from models.admin import Admin
from models.employee import Employee
from models.officer import FinanceOfficer
from models.monitor import Monitor
from models.applicant import Applicant

VALID_STATUSES = ['BANNED', 'INACTIVE', 'DEACTIVATED']

def ban_user(admin_id, user_id, status):
    try:
        if not account_checker(admin_id):
            return {'message': 'Admin user does not exist'}, 404

        user = (
            Applicant.query.filter_by(id=user_id).first() or
            Admin.query.filter_by(id=user_id).first() or
            Employee.query.filter_by(id=user_id).first() or
            FinanceOfficer.query.filter_by(id=user_id).first() or 
            Monitor.query.filter_by(id=user_id).first()
        )
        
        if not user:
            return {'message': 'User does not exist'}, 404

        if status not in VALID_STATUSES:
            return {'message': 'Select a valid status'}, 400

        if user.status == status:
            return {'message': f'User already {status}'}, 409

        if hasattr(user, 'role') and user.role == 'SUPER_ADMIN':
            return {'message': 'Cannot modify SUPER_ADMIN account'}, 403

        user.status = status

        db.session.commit()

        log_applicant_track(
            admin_id,
            'ADMIN',
            f'Admin set user {user_id} status to {status}'
        )

        return {
            'message': f'User {status} successfully',
            'user_id': user_id,
            'status': status
        }, 200
    
    except Exception as e:
        db.session.rollback()
        print(f'User status update error: {e}')
        return {'message': 'Something went wrong'}, 500