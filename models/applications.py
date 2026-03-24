from database import db
from sqlalchemy.sql import func
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from sqlalchemy.types import DateTime
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from functions.time_zone_fix import local_now

class Applications(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.String)
    funding_window_id = db.Column(db.String)
    applicant_id = db.Column(db.String)
    programme_title = db.Column(db.String)
    programme_decription = db.Column(db.Text)
    category = db.Column(db.String)
    type = db.Column(db.String)
    required_funding = db.Column(db.Double)
    number_of_learners = db.Column(db.Integer)
    cost_per_learner = db.Column(db.Double)
    start_date = db.Column(db.String)
    end_date = db.Column(db.String)
    duration = db.Column(db.String)
    proposal_doc = db.Column(db.String)
    application_status = db.Column(db.String)
    is_approved = db.Column(db.Boolean, default=False)
    approved_by = db.Column(db.String, default=None)
    created_at = db.Column(DateTime(timezone=True), default=local_now)