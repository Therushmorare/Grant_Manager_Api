from database import db
from functions.form_sanitizer import sanitize_input
from functions.user_logs import log_applicant_track

"""
Edit contact person
"""
def edit_contact_person(
    applicant_id,
    contact_id,
    name=None,
    email=None,
    phone=None,
    role=None
):
    try:
        #Validate applicant
        applicant = Applicant.query.filter_by(id=applicant_id).first()
        if not applicant:
            return {'message': 'Applicant does not exist'}, 404

        #Fetch contact
        contact = ContactPersons.query.filter_by(
            contact_id=contact_id,
            applicant_id=applicant_id
        ).first()

        if not contact:
            return {'message': 'Contact person not found'}, 404

        #Track changes (optional but powerful)
        changes = []

        #Update fields (partial updates)

        if name:
            clean_name = sanitize_input(name).strip()
            if clean_name:
                contact.name = clean_name
                changes.append("name")

        if email:
            clean_email = sanitize_input(email).strip().lower()

            if "@" not in clean_email:
                return {'message': 'Invalid email format'}, 400

            # 🔒 Prevent duplicate emails
            existing = ContactPersons.query.filter(
                ContactPersons.email == clean_email,
                ContactPersons.contact_id != contact_id,
                ContactPersons.applicant_id == applicant_id
            ).first()

            if existing:
                return {'message': 'Email already used for another contact'}, 409

            contact.email = clean_email
            changes.append("email")

        if phone:
            clean_phone = sanitize_input(phone).strip()
            if clean_phone:
                contact.phone = clean_phone
                changes.append("phone")

        if role:
            clean_role = sanitize_input(role).strip()
            if clean_role:
                contact.role = clean_role
                changes.append("role")

        #Prevent empty update
        if not changes:
            return {'message': 'No valid fields provided for update'}, 400

        db.session.commit()

        #Log activity
        log_applicant_track(
            applicant_id,
            'APPLICANT',
            f'Applicant:{applicant_id} updated contact:{contact_id} fields:{",".join(changes)}'
        )

        return {
            'message': 'Contact updated successfully',
            'updated_fields': changes
        }, 200

    except Exception as e:
        db.session.rollback()
        print(f'Edit contact error: {e}')

        return {
            'message': 'Failed to update contact',
            'error': str(e)
        }, 500