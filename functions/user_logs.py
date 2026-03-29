from flask import Flask, render_template, request, url_for, redirect,send_from_directory, jsonify,session, flash
from database import db
from datetime import datetime
from models.logs import UserLogs
from models.admin import Admin
from models.employee import Employee
from models.officer import FinanceOfficer
from models.monitor import Monitor
from models.applicant import Applicant

"""
Capture all user logs throughout the app
"""

#user logs
def log_applicant_track(user_id, user_type, action_type):
    try:
        user = Admin.query.filter_by(id=user_id).first() or \
                Employee.query.filter_by(id=user_id).first() or \
                FinanceOfficer.query.filter_by(id=user_id).first() or \
                Monitor.query.filter_by(id=user_id).first() or \
                Applicant.query.filter_by(id=user_id).first()


        if not user:
            raise ValueError(f"User {user_id} not found")

        save_data = UserLogs(
            user_id=user_id,
            applicant_type=user_type,
            action=action_type
        )

        db.session.add(save_data)
        db.session.commit()

        print("User action added to logs")

    except Exception as e:
        db.session.rollback()
        print(f"Log Error: {e}")