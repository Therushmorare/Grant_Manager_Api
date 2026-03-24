import random
from datetime import datetime, timedelta, timezone
from database import db
from models.mfa_table import mfaCode
from functions.celery_worker import celery_ext

@celery_ext.celery.task
def cleanup_expired_mfa_codes():
    try:
        now = datetime.now(timezone.utc)
        # Delete all expired codes in one query
        mfaCode.query.filter(mfaCode.expires_at < now).delete(synchronize_session=False)
        db.session.commit()
    except Exception as e:
        print(f"[MFA Cleanup Error] {e}")
        db.session.rollback()