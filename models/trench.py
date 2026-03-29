from database import db
from sqlalchemy.sql import func
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from sqlalchemy.types import DateTime
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from functions.time_zone_fix import local_now

class TrenchPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.String)
    officer_id = db.Column(db.String)
    trench_id = db.Column(db.String)
    trench = db.Column(db.Integer)
    percentage = db.Column(db.Double)
    sequence = db.Column(db.Integer)
    status = db.Column(db.String)
    created_at = db.Column(DateTime(timezone=True), default=local_now)
