from database import db
from sqlalchemy.sql import func
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from sqlalchemy.types import DateTime
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from functions.time_zone_fix import local_now

class SiteVisit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    officer_id = db.Column(db.String)
    assigned_to = db.Column(db.String)
    application_id = db.Column(db.String)
    visit_id = db.Column(db.String)
    date = db.Column(db.String)
    time = db.Column(db.String)
    location = db.Column(db.String)
    status = db.Column(db.String)
    created_at = db.Column(DateTime(timezone=True), default=local_now)
