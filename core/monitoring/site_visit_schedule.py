from database import db
from functions.user_logs import log_applicant_track
from core.auth.account_checker import account_checker
from functions.form_sanitizer import sanitize_input
from datetime import datetime
import uuid
from models.applications import Applications
from functions.time_zone_fix import local_now
from datetime import datetime, timedelta, timezone
from models.visit import SiteVisit

"""
Monitor approved application via site visits
"""
def schedule_visit(officer_id, application_id, date, time, location, assigned_to):
    try:
        #Validate officer
        if not account_checker(officer_id):
            return {'message': 'Officer does not exist'}, 404
        
        #Validate application
        application = Applications.query.filter_by(application_id=application_id).first()
        if not application:
            return {'message': 'Application does not exist'}, 404
        
        if application.final_status != 'APPROVED':
            return {'message': 'Only approved applications can be monitored'}, 400
        
        #Validate assigned monitor
        if not account_checker(assigned_to):
            return {'message': 'Assigned monitor does not exist'}, 404

        #Validate inputs
        if any(x is None for x in [date, time, location]):
            return {'message': 'Please fill out all inputs'}, 400
        
        #Validate datetime (no past scheduling)
        try:
            visit_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        except ValueError:
            return {'message': 'Invalid date/time format. Use YYYY-MM-DD HH:MM'}, 400
        
        if visit_datetime < datetime.now(timezone.utc):
            return {'message': 'Cannot schedule a visit in the past'}, 400

        visit_id = str(uuid.uuid4())

        #Save visit
        save_data = SiteVisit(
            officer_id=officer_id,
            assigned_to=assigned_to,
            application_id=application_id,
            visit_id=visit_id,
            date=date,
            time=time,
            location=sanitize_input(location),
            status='SCHEDULED'
        )

        db.session.add(save_data)
        db.session.commit()

        #Log
        log_applicant_track(
            officer_id,
            'MONITORER',
            f'Scheduled site visit for application: {application_id}'
        )

        return {
            'message': 'Site visit scheduled successfully',
            'visit_id': visit_id
        }, 200

    except Exception as e:
        db.session.rollback()
        print(f'Site visit schedule error: {e}')
        return {'message': 'Something went wrong'}, 500