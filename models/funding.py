from database import db
from sqlalchemy.sql import func
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from sqlalchemy.types import DateTime
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from functions.time_zone_fix import local_now

class Funding(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    applicant_id = db.Column(db.String)
    applicantion_id = db.Column(db.String)
    funding_window_id = db.Column(db.String)
    approved_funding = db.Column(db.Double)
    status = db.Column(db.String)
    notes = db.Column(db.Text)
    approved_id = db.Column(db.String)
    created_at = db.Column(DateTime(timezone=True), default=local_now)