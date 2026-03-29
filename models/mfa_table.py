from datetime import datetime, timedelta, timezone
from database import db

class mfaCode(db.Model):
    __tablename__ = 'mfa_codes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, nullable=False, index=True)
    user_type = db.Column(db.String, nullable=False)

    code = db.Column(db.String(10), nullable=False)
    attempts = db.Column(db.Integer, default=0)
    verified = db.Column(db.Boolean, default=False)

    expires_at = db.Column(db.DateTime(timezone=True), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))