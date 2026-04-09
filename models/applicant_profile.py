from database import db
from sqlalchemy.sql import func
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from sqlalchemy.types import DateTime
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from functions.time_zone_fix import local_now

"""
Applicant Profile
"""

class ApplicantProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.String)
    applicant_id = db.Column(db.String)
    legal_name = db.Column(db.String)
    trading_name = db.Column(db.String)
    registration_number = db.Column(db.String)
    company_type = db.Column(db.String)
    industry = db.Column(db.String)
    seta_affiliation = db.Column(db.String)
    registered_address = db.Column(db.String)
    physical_address = db.Column(db.String)
    city = db.Column(db.String)
    province = db.Column(db.String)
    postal_code = db.Column(db.String)
    country = db.Column(db.String)
    verification_status = db.Column(db.String)
    is_verified = db.Column(db.Boolean, default=False)
    verified_by = db.Column(db.String)
    created_at = db.Column(DateTime(timezone=True), default=local_now)