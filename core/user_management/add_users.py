from core.auth.account_checker import account_checker
from functions.random_string import generate_random_string
from core.auth.email_sender import send_credentials
from database import db
import uuid
from extensions import bcrypt
from functions.form_sanitizer import sanitize_input
from functions.user_logs import log_applicant_track
from models.admin import Admin
from models.employee import Employee
from models.officer import FinanceOfficer
from models.monitor import Monitor

USER_TYPES = ['ADMIN', 'SUPER_ADMIN', 'FINANCE_OFFICER', 'EMPLOYEE', 'MONITOR']
VALID_ROLE = ['ADMIN', 'SUPER_ADMIN', 'FINANCE_OFFICER', 'EMPLOYEE', 'MONITOR', 'MANAGER']

def add_users(user_type, first_name, last_name, email, phone_number, role, department, employee_number, admin_id=None):
    try:
        if any(x is None for x in [user_type, first_name, last_name, email, phone_number, role, department, employee_number]):
            return {'message': 'Please fill out all inputs'}, 400
        
        if user_type not in USER_TYPES:
            return {'message': 'Select valid user type'}, 400
            
        if role not in VALID_ROLE:
            return {'message': 'Select a valid user role'}, 400

        existing_user = (
            Admin.query.filter_by(email=email).first() or
            FinanceOfficer.query.filter_by(email=email).first() or
            Employee.query.filter_by(email=email).first() or
            Monitor.query.filter_by(email=email).first()
        )

        if existing_user:
            return {'message': 'User with this email already exists'}, 409

        if admin_id:
            if not account_checker(admin_id):
                return {'message': 'Admin user does not exist'}, 404

        user_id = str(uuid.uuid4())
        password = generate_random_string(10)
        hash_password = bcrypt.generate_password_hash(password).decode('utf-8')

        first_name = sanitize_input(first_name)
        last_name = sanitize_input(last_name)
        email = sanitize_input(email)
        phone_number = sanitize_input(phone_number)
        role = sanitize_input(role)
        department = sanitize_input(department)
        employee_number = sanitize_input(employee_number)

        save_user = None

        if user_type in ['ADMIN', 'SUPER_ADMIN']:
            save_user = Admin(
                id=user_id,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone_number=phone_number,
                role=role,
                department=department,
                employee_number=employee_number,
                password=hash_password,
                status='ACTIVE',
                mfa_required=True,
                is_verified=True,
                is_active=True
            )

        elif user_type == 'FINANCE_OFFICER':
            save_user = FinanceOfficer(
                id=user_id,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone_number=phone_number,
                role=role,
                department=department,
                employee_number=employee_number,
                password=hash_password,
                status='ACTIVE',
                mfa_required=True,
                is_verified=True,
                is_active=True
            )

        elif user_type == 'EMPLOYEE':
            save_user = Employee(
                id=user_id,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone_number=phone_number,
                role=role,
                department=department,
                employee_number=employee_number,
                password=hash_password,
                status='ACTIVE',
                mfa_required=True,
                is_verified=True,
                is_active=True
            )

        elif user_type == 'MONITOR':
            save_user = Monitor(
                id=user_id,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone_number=phone_number,
                role=role,
                department=department,
                employee_number=employee_number,
                password=hash_password,
                status='ACTIVE',
                mfa_required=True,
                is_verified=True,
                is_active=True
            )

        else:
            return {'message': 'Invalid user type'}, 400

        db.session.add(save_user)
        db.session.commit()

        send_credentials(email, employee_number, first_name, last_name, password)

        if admin_id:
            log_applicant_track(
                admin_id,
                'ADMIN',
                f'Admin created user {user_type} with ID: {user_id}'
            )

        return {
            'message': 'User added successfully',
            'user_id': user_id
        }, 200

    except Exception as e:
        db.session.rollback()
        print(f'User add error: {e}')
        return {'message': 'Something went wrong'}, 500