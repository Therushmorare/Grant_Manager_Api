from models.admin import Admin
from models.employee import Employee
from models.applicant import Applicant
from models.officer import FinanceOfficer
from models.monitor import Monitor

def account_checker(user_id):
    try:
        user = (
            Applicant.query.filter_by(id=user_id).first() or
            Admin.query.filter_by(id=user_id).first() or
            Employee.query.filter_by(id=user_id).first() or
            FinanceOfficer.query.filter_by(id=user_id).first() or 
            Monitor.query.filter_by(id=user_id).first()
        )

        return user is not None

    except Exception as e:
        print(f'Account Checker Error: {e}')
        return False