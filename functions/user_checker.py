from functions.form_sanitizer import sanitize_input

#check user accounts
def check_users(email):
    try:
        san_email = sanitize_input(email)
        sources = {
            'EMPLOYEE': Employee,
            'ADMIN': Admin,
            'APPLICANT': Applicant,
            'FINANCE': FinanceOfficer
        }

        for role, model in sources.items():
            user = model.query.filter_by(email=san_email).first()
            if user:
                return {
                    'message': f'Email already registered as {role}',
                    'exists': True,
                    'role': role
                }, 409

        return {
            'message': 'Email is available',
            'exists': False
        }, 200

    except Exception as e:
        print(f'User check error: {e}')
        return {'message': 'Error checking email'}, 500