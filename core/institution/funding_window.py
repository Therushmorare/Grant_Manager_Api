from functions.form_sanitizer import sanitize_input
from datetime import datetime
import uuid
from database import db
from functions.user_logs import log_applicant_track

def create_funding_window(
    user_id,
    grant_name,
    grant_description,
    available_funding,
    grant_categories_list,
    requirements_list,
    deadline
):
    try:
        # Validate user
        user = Employee.query.filter_by(employee_id=user_id).first()

        if not user:
            return {'message': 'User does not exist'}, 404
        
        if user.role != 'EMPLOYEE':
            return {'message': 'You dont have permission to perform action!'}, 403
        
        # Validate inputs (stronger)
        if not all([
            grant_name, grant_description, available_funding,
            grant_categories_list, requirements_list, deadline
        ]):
            return {'message': 'Please ensure all fields are filled'}, 400

        #Sanitize inputs
        gname = sanitize_input(grant_name)
        gdescription = sanitize_input(grant_description)
        gfunding = sanitize_input(str(available_funding))

        # Clean lists properly
        cleaned_categories = [
            sanitize_input(c.strip())
            for c in grant_categories_list
            if isinstance(c, str) and c.strip()
        ]

        cleaned_requirements = [
            sanitize_input(r.strip())
            for r in requirements_list
            if isinstance(r, str) and r.strip()
        ]

        #Ensure deadline is datetime
        if isinstance(deadline, str):
            deadline = datetime.fromisoformat(deadline)

        if deadline < datetime.now():
            return {'message': 'Deadline date cannot be a past date'}, 400

        #Generate ID
        funding_window_id = str(uuid.uuid4())

        # Save funding window
        save_data = FundingWindow(
            funding_window_id=funding_window_id,
            poster_id=user_id,
            name=gname,
            description=gdescription,
            funding=gfunding,
            deadline=deadline,
            status='PENDING'
        )

        db.session.add(save_data)

        #Save requirements
        if cleaned_requirements:
            new_requirements = [
                Requirements(
                    poster_id=user_id,
                    funding_window_id=funding_window_id,
                    requirement=r
                )
                for r in cleaned_requirements
            ]
            db.session.add_all(new_requirements)

        #Save categories
        if cleaned_categories:
            new_categories = [
                Categories(
                    poster_id=user_id,
                    funding_window_id=funding_window_id,
                    category=c
                )
                for c in cleaned_categories
            ]
            db.session.add_all(new_categories)

        db.session.commit()

        #Log activity
        log_applicant_track(
            user_id,
            'EMPLOYEE',
            f'Employee:{user_id} created funding window ID:{funding_window_id}'
        )

        return {
            'message': 'Funding window has been added successfully',
            'application_id': funding_window_id
        }, 201

    except Exception as e:
        db.session.rollback()
        print(f'Funding Window Error: {e}')

        return {
            'message': 'Failed to create funding window',
            'error': str(e)
        }, 500