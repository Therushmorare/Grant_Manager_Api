from database import db
from sqlalchemy.sql import func
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from sqlalchemy.types import DateTime
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from functions.time_zone_fix import local_now

class Requirements(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    poster_id = db.Column(db.String)
    funding_window_id = db.Column(db.String)
    requirement = db.Column(db.Text)
    created_at = db.Column(DateTime(timezone=True), default=local_now)

class Categories(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    poster_id = db.Column(db.String)
    funding_window_id = db.Column(db.String)
    category = db.Column(db.Text)
    created_at = db.Column(DateTime(timezone=True), default=local_now)