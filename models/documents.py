from database import db
from sqlalchemy.sql import func
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from sqlalchemy.types import DateTime
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from functions.time_zone_fix import local_now

"""
Documents
"""

class ApplicantDocuments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    applicant_id = db.Column(db.String)
    doc_id = db.Column(db.String)
    type = db.Column(db.String)
    document = db.Column(db.String)
    verification_status = db.Column(db.String)
    is_verified = db.Column(db.Boolean, default=False)
    verified_by = db.Column(db.String)
    created_at = db.Column(DateTime(timezone=True), default=local_now)