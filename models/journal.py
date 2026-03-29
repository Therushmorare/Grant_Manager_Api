from database import db
from sqlalchemy.sql import func
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from sqlalchemy.types import DateTime
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from functions.time_zone_fix import local_now

class TransactionJournal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    entry_id = db.Column(db.String)
    trench_id = db.Column(db.String)
    request_id = db.Column(db.String)
    amount = db.Column(db.Double)
    status = db.Column(db.String)
    statement = db.Column(db.Text)
    created_at = db.Column(DateTime(timezone=True), default=local_now)