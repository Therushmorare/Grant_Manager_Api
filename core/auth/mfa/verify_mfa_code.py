from flask import session
import random
from datetime import datetime, timedelta, timezone
from database import db
from models.mfa_table import mfaCode
from hmac import compare_digest

MAX_MFA_ATTEMPTS = 5

def verify_mfa_code(user_id, code):
    try:
        if not user_id or not code:
            return False, "Invalid request"

        mfa_record = (
            mfaCode.query
            .filter_by(user_id=user_id, verified=False)
            .order_by(mfaCode.created_at.desc())
            .first()
        )

        if not mfa_record:
            return False, "Invalid or expired code"

        if mfa_record.attempts >= MAX_MFA_ATTEMPTS:
            return False, "Too many attempts. Request new code."

        if mfa_record.expires_at < datetime.now(timezone.utc):
            return False, "Code expired"

        if not compare_digest(mfa_record.code, str(code).strip()):
            mfa_record.attempts += 1
            db.session.commit()
            return False, "Invalid code"

        mfa_record.verified = True
        db.session.commit()

        return True, "MFA verified"

    except Exception as e:
        print(f"[MFA ERROR] {type(e).__name__}: {e}")
        return False, "Something went wrong"