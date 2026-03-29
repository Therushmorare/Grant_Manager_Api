from database import db
from sqlalchemy.sql import func
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from sqlalchemy.types import DateTime
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from functions.time_zone_fix import local_now

class PaymentRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    applicant_id = db.Column(db.String)
    trench_id = db.Column(db.String)
    request_id = db.Column(db.String)
    report = db.Column(db.String)
    payment_request = db.Column(db.Double)
    status = db.Column(db.String)
    is_approved = db.Column(db.Boolean, default=False)
    approved_by = db.Column(db.String)
    comments = db.Column(db.Text)
    created_at = db.Column(DateTime(timezone=True), default=local_now)