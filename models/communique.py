from database import db
from sqlalchemy.sql import func
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from sqlalchemy.types import DateTime
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from functions.time_zone_fix import local_now

class Communique(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.String)
    sender_id = db.Column(db.String)
    receiver_id = db.Column(db.String)
    subject = db.Column(db.String)
    message = db.Column(db.Text)
    status = db.Column(db.String)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(DateTime(timezone=True), default=local_now)