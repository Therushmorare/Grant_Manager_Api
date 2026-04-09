from flask import Flask, render_template, request, url_for, redirect,send_from_directory, jsonify,session, flash
from itsdangerous import URLSafeTimedSerializer
from database import db
import datetime
import uuid
from extensions import bcrypt
from .verification_sender import *
import os
from flask_mail import Mail, Message
from mail_util import mail
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from models.applicant import ExternalApplicant, InternalApplicant
import secrets
from flask_jwt_extended import create_access_token
from datetime import timedelta
from functions.form_sanitizer import sanitize_input
from models.admin import Admin
from models.employee import Employee
from models.applicant import Applicant
from models.officer import FinanceOfficer
from models.monitor import Monitor

"""
User Login
"""
types = ["applicant", "employee", "monitor", "officer", "admin", "super_admin"]
MAX_ATTEMPTS = 5 #for login purposes

def signin_users(email, password, user_type):
    try:
        # Initialize login attempts
        if 'login_attempts' not in session:
            session['login_attempts'] = 0

        if session['login_attempts'] >= MAX_ATTEMPTS:
            return {"message": "Too many login attempts, your account will be temporarily locked. Please try again later."}, 429

        if not email or not password or not user_type:
            return {"message": "Email, password, and user type are required"}, 400

        #check user type
        if user_type not in types:
            return {'message': 'Invalid user type'}, 400
        
        # Sanitize input
        safe_email = sanitize_input(email)

        # Fetch accounts
        user = (
                    Applicant.query.filter_by(email=email).first() or
                    Admin.query.filter_by(email=email).first() or
                    Employee.query.filter_by(email=email).first() or
                    FinanceOfficer.query.filter_by(email=email).first() or 
                    Monitor.query.filter_by(email=email).first()
                )
        
        # Generic error to prevent enumeration
        if not user or not bcrypt.check_password_hash(user.password, password):
            session['login_attempts'] += 1
            return {"message": "Invalid email or password"}, 403

        # Check account confirmation
        if str(user.is_verified) != True:
            return {"message": "Please verify your account before logging in"}, 403

        # Reset login attempts after successful login
        session.pop('login_attempts', None)

        # Perform login
        login_user(user)

        # Generate JWT
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={"role": f"{user_type.lower()}_applicant"},
            expires_delta=timedelta(hours=24)
        )

        return {
            "message": "User logged in successfully",
            "email": safe_email,
            "user_type": user_type.lower(),
            "user_id": user.id,
            "access_token": access_token
        }, 200

    except Exception as e:
        print(f"[Signin Error] {type(e).__name__}: {e}")
        return {"message": "Something went wrong"}, 500