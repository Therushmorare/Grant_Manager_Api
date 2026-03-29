from database import db
from sqlalchemy.sql import func
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from sqlalchemy.types import DateTime
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from functions.time_zone_fix import local_now

class Inspection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    applicantion_id = db.Column(db.String)
    visit_id = db.Column(db.String)
    monitor_id = db.Column(db.String)
    status = db.Column(db.String)
    comments = db.Column(db.Text)
    file_id = db.Column(db.String)
    file = db.Column(db.String)
    created_at = db.Column(DateTime(timezone=True), default=local_now)