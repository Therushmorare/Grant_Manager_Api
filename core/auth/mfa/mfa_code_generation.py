import random
from datetime import datetime, timedelta, timezone
from database import db
from models.mfa_table import mfaCode
from flask import session

def generate_mfa_code(length=6):
    return ''.join(str(random.randint(0, 9)) for _ in range(length))


#Save MFA code (invalidate old ones)
def save_mfa_code(user_id, user_type, ttl_minutes=5):
    # Invalidate previous codes
    mfaCode.query.filter_by(user_id=user_id, verified=False).update({
        "verified": True
    })

    code = generate_mfa_code()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=ttl_minutes)

    mfa = mfaCode(
        user_id=user_id,
        user_type=user_type,
        code=code,
        expires_at=expires_at
    )

    db.session.add(mfa)
    db.session.commit()

    return code