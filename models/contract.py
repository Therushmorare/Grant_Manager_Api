from database import db
from sqlalchemy.types import DateTime
from functions.time_zone_fix import local_now

class ContractAgreement(db.Model):
    __tablename__ = "contract_agreements"

    id = db.Column(db.Integer, primary_key=True)
    contract_id = db.Column(db.String(255), unique=True, nullable=False)
    applicant_id = db.Column(db.String, nullable=False)
    application_id = db.Column(db.String, nullable=False)
    contract = db.Column(db.String(255), nullable=False)  # file URL
    shared_by = db.Column(db.String, nullable=False)

    contract_status = db.Column(db.String(50), default="PENDING")  # PENDING / SIGNED
    is_signed = db.Column(db.Boolean, default=False)

    created_at = db.Column(DateTime(timezone=True), default=local_now)
    updated_at = db.Column(DateTime(timezone=True), default=local_now, onupdate=local_now)


class ContractSignature(db.Model):
    __tablename__ = "contract_signatures"

    id = db.Column(db.Integer, primary_key=True)
    contract_id = db.Column(db.String(255), nullable=False)
    signer_name = db.Column(db.String(255), nullable=False)
    signer_email = db.Column(db.String(255), nullable=False)
    signature_data = db.Column(db.Text, nullable=False)  # e.g., base64 image or digital hash
    signed_at = db.Column(DateTime(timezone=True), default=local_now)