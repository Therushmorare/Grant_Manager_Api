from database import db
from core.auth.account_checker import account_checker
from functions.form_sanitizer import sanitize_input
from functions.user_logs import log_applicant_track
from models.admin import Admin
from models.employee import Employee
from models.officer import FinanceOfficer
from models.monitor import Monitor
from models.applicant import Applicant

USER_TYPES = ['ADMIN', 'SUPER_ADMIN', 'FINANCE_OFFICER', 'EMPLOYEE', 'MONITOR']

def edit_user(
    admin_id,
    user_id,
    user_type,
    first_name=None,
    last_name=None,
    email=None,
    phone_number=None,
    role=None,
    department=None,
    employee_number=None,
    status=None
):
    try:
        if not account_checker(admin_id):
            return {'message': 'Admin does not exist'}, 404

        if user_type not in USER_TYPES:
            return {'message': 'Invalid user type'}, 400

        user = None

        if user_type in ['ADMIN', 'SUPER_ADMIN']:
            user = Admin.query.filter_by(id=user_id).first()

        elif user_type == 'FINANCE_OFFICER':
            user = FinanceOfficer.query.filter_by(id=user_id).first()

        elif user_type == 'EMPLOYEE':
            user = Employee.query.filter_by(id=user_id).first()

        elif user_type == 'MONITOR':
            user = Monitor.query.filter_by(id=user_id).first()

        if not user:
            return {'message': 'User not found'}, 404

        if email and email != user.email:
            existing_user = (
                Admin.query.filter_by(email=email).first() or
                FinanceOfficer.query.filter_by(email=email).first() or
                Employee.query.filter_by(email=email).first() or
                Monitor.query.filter_by(email=email).first()
            )

            if existing_user:
                return {'message': 'Email already in use'}, 409

        if first_name:
            user.first_name = sanitize_input(first_name)

        if last_name:
            user.last_name = sanitize_input(last_name)

        if email:
            user.email = sanitize_input(email)

        if phone_number:
            user.phone_number = sanitize_input(phone_number)

        if role:
            user.role = sanitize_input(role)

        if department:
            user.department = sanitize_input(department)

        if employee_number:
            user.employee_number = sanitize_input(employee_number)

        if status:
            user.status = sanitize_input(status)

        db.session.commit()

        log_applicant_track(
            admin_id,
            'ADMIN',
            f'Admin updated user {user_id} ({user_type})'
        )

        return {
            'message': 'User updated successfully',
            'user_id': user_id
        }, 200

    except Exception as e:
        db.session.rollback()
        print(f'Edit user error: {e}')
        return {'message': 'Something went wrong'}, 500