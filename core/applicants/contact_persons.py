from database import db
from functions.form_sanitizer import sanitize_input
from functions.domain_validation import check_domain
from functions.user_logs import log_applicant_track
import uuid
from models.contact_person import ContactPersons
from models.applicant import Applicant
from core.auth.account_checker import account_checker

"""
Add contact persons
"""

DOMAINS = ["gmail.com", "outlook.com", "yahoo.com"]

def add_contact_person(applicant_id, names_list, emails_list, phone_list, role_list):
    try:
        # Validate applicant        
        if not account_checker(applicant_id):
            return {'message': 'Applicant does not exist'}, 404
        
        #Default empty lists
        names_list = names_list or []
        emails_list = emails_list or []
        phone_list = phone_list or []
        role_list = role_list or []

        #Validate list lengths
        if not (len(names_list) == len(emails_list) == len(phone_list) == len(role_list)):
            return {'message': 'Input lists must be of equal length'}, 400

        new_contacts = []

        for name, email, phone, role in zip(
            names_list,
            emails_list,
            phone_list,
            role_list
        ):
            #Safe checks
            if not all([name, email, phone, role]):
                continue

            name = sanitize_input(name).strip()
            email = sanitize_input(email).strip().lower()
            phone = sanitize_input(phone).strip()
            role = sanitize_input(role).strip()

            if not all([name, email, phone, role]):
                continue

            #check if domain is valid
            check_domain(email, DOMAINS)

            new_contacts.append(
                ContactPersons(
                    applicant_id=applicant_id,
                    contact_id=str(uuid.uuid4()),
                    name=name,
                    email=email,
                    phone=phone,
                    role=role
                )
            )

        #Prevent wiping data if no valid contacts
        if not new_contacts:
            return {'message': 'No valid contact persons provided'}, 400

        #Replace existing contacts (SAFE)
        ContactPersons.query.filter_by(applicant_id=applicant_id).delete()

        db.session.add_all(new_contacts)
        db.session.commit()

        #Log activity
        log_applicant_track(
            applicant_id,
            'APPLICANT',
            f'Applicant:{applicant_id} updated contact persons ({len(new_contacts)} contacts)'
        )

        return {
            'message': 'Contact persons added successfully',
            'count': len(new_contacts)
        }, 200

    except Exception as e:
        db.session.rollback()
        print(f'Contact person add error: {e}')

        return {
            'message': 'Failed to add contact persons',
            'error': str(e)
        }, 500