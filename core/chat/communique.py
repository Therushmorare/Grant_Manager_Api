from core.auth.account_checker import account_checker
import uuid
from functions.form_sanitizer import sanitize_input
from database import db
from functions.user_logs import log_applicant_track
from datetime import datetime

def send_users_communique(user_id, applicant_id, subject, message):
    try:
        if not account_checker(user_id):
            return {'message': 'Sender does not exist'}, 404
        
        if not account_checker(applicant_id):
            return {'message': 'Receiver does not exist'}, 404
        
        if user_id == applicant_id:
            return {'message': 'Cannot send message to yourself'}, 400
        
        if not subject or not subject.strip():
            return {'message': 'Subject cannot be empty'}, 400
        
        if not message or not message.strip():
            return {'message': 'Message cannot be empty'}, 400
        
        subject = sanitize_input(subject.strip())
        message = sanitize_input(message.strip())

        message_id = str(uuid.uuid4())
        now = datetime.utcnow()

        save_data = Communique(
            message_id=message_id,
            sender_id=user_id,
            receiver_id=applicant_id,
            subject=subject,
            message=message,
            status='SENT',
            is_read=False,
            created_at=now
        )

        db.session.add(save_data)
        db.session.commit()

        log_applicant_track(
            user_id,
            'USER',
            f'Message sent to {applicant_id} with subject: "{subject}"'
        )

        return {
            'message': 'Communique sent successfully',
            'data': {
                'message_id': message_id,
                'sender_id': user_id,
                'receiver_id': applicant_id,
                'subject': subject,
                'status': 'SENT',
                'created_at': str(now)
            }
        }, 200
    
    except Exception as e:
        db.session.rollback()
        print(f'Communique error: {e}')
        return {'message': 'Something went wrong'}, 500