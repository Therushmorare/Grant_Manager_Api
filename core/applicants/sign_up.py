from functions.form_sanitizer import sanitize_input
from functions.domain_validation import check_domain
from functions.user_checker import check_users
from database import db
import uuid
from extensions import bcrypt
from core.auth.verification_sender import *
import os
from flask_mail import Mail, Message
from mail_util import mail
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from core.auth.email_sender import *

"""
Applicant Signup
"""
DOMAINS = ["gmail.com", "outlook.com", "yahoo.com"]

def applicant_signup(email, password):
    try:
        if email is None:
            return {'message': 'Please enter email'}, 400
        
        if password is None:
            return {'message': 'Please enter password'}, 400
        
        #check if domain is valid
        check_domain(email, DOMAINS)

        #check if account exists
        check_users(email)

        user_id = str(uuid.uuid4())

        hashed_password = bcrypt.generate_password_hash(sanitize_input(password)).decode('utf-8')

        save_user = Applicant(
            id=user_id,
            email=sanitize_input(email),
            password=hashed_password,
            status='UNVERIFIED',
            is_verified=False,
            is_active=False
        )

        db.session.add(save_user)
        db.session.commit()

        # Send verification code
        send_verification_code(email)

        return {"message": "A verification code was sent to your email, please verify your account"}, 200
    
    except Exception as e:
        db.session.rollback()
        print(f'Signup error:{e}')
        return {'message': 'Something went wrong'}, 500
