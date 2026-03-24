from flask import Flask, render_template, request, url_for, redirect,send_from_directory, jsonify,session, flash
from itsdangerous import URLSafeTimedSerializer
import random
from flask import current_app
from redis_config import redis_client
from flask_mail import Mail, Message
from mail_util import mail
from database import db
from flask import jsonify
from .email_sender import send_verification_email
from models.applicant import ExternalApplicant, InternalApplicant
from functions.string_sanitizer import escape_ldap_input
"""
Send verification code and verify it
"""    
MAX_OTP_ATTEMPTS = 5

def send_verification_code(email):
    verification_code = random.randint(100000, 999999)
    redis_client.setex(f"otp:{email}", 300, str(verification_code))  # Store as string

    #send via email here instead of returning
    send_verification_email(email, verification_code)

def verify_token(user_email, token):
    try:
        if not user_email or not token:
            return {"message": "Email and OTP token are required"}, 400

        # Sanitize input
        safe_email = escape_ldap_input(user_email)
        user_otp = str(token).strip()

        # Look for user in both tables
        user = ExternalApplicant.query.filter_by(email=safe_email).first() or \
               InternalApplicant.query.filter_by(email=safe_email).first()

        # Generic error message to prevent user enumeration
        if not user:
            return {"message": "Invalid OTP or email"}, 401

        # Track OTP attempts in Redis to prevent brute-force
        otp_attempts_key = f"otp_attempts:{safe_email}"
        attempts = redis_client.get(otp_attempts_key)
        attempts = int(attempts.decode("utf-8")) if attempts else 0

        if attempts >= MAX_OTP_ATTEMPTS:
            return {"message": "Too many OTP attempts, please request a new one"}, 429

        # Retrieve OTP from Redis
        stored_otp = redis_client.get(f"otp:{safe_email}")
        if stored_otp:
            stored_otp = stored_otp.decode("utf-8") if isinstance(stored_otp, bytes) else str(stored_otp)

        # Compare OTPs
        if stored_otp and user_otp == stored_otp:
            user.confirmation_status = 'True'
            db.session.commit()
            redis_client.delete(f"otp:{safe_email}")
            redis_client.delete(otp_attempts_key)  # reset attempt count
            return {"message": "Verification Successful", "user_id": user.applicant_id}, 200

        # Increment OTP attempts
        redis_client.incr(otp_attempts_key)
        redis_client.expire(otp_attempts_key, 3600)  # expire after 1 hour

        return {"message": "Invalid OTP or email"}, 401

    except Exception as e:
        print(f"[OTP Verification Error] {type(e).__name__}: {e}")
        return {"message": "Something went wrong"}, 500