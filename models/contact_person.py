from database import db
from sqlalchemy.sql import func
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from sqlalchemy.types import DateTime
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from functions.time_zone_fix import local_now

"""
Contact Person
"""

class ContactPersons(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    applicant_id = db.Column(db.String)
    contact_id = db.Column(db.String)
    name = db.Column(db.String)
    email = db.Column(db.String)
    phone = db.Column(db.String)
    role = db.Column(db.String)
