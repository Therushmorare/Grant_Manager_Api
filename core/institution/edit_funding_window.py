from functions.form_sanitizer import sanitize_input
from datetime import datetime
from database import db
from functions.user_logs import log_applicant_track

def edit_funding_window(
    user_id,
    funding_window_id,
    grant_name=None,
    grant_description=None,
    available_funding=None,
    grant_categories_list=None,
    requirements_list=None,
    deadline=None,
    status=None
):
    try:
        #Validate user
        user = Employee.query.filter_by(employee_id=user_id).first()

        if not user:
            return {'message': 'User does not exist'}, 404
        
        if user.role != 'EMPLOYEE':
            return {'message': 'You dont have permission to perform action!'}, 403

        #Fetch funding window
        funding = FundingWindow.query.filter_by(funding_window_id=funding_window_id).first()

        if not funding:
            return {'message': 'Funding window not found'}, 404

        #Ensure ownership (VERY IMPORTANT)
        if funding.poster_id != user_id:
            return {'message': 'Unauthorized to edit this funding window'}, 403

        #Update fields ONLY if provided
        if grant_name:
            funding.name = sanitize_input(grant_name)

        if grant_description:
            funding.description = sanitize_input(grant_description)

        if available_funding:
            funding.funding = sanitize_input(str(available_funding))

        if deadline:
            if isinstance(deadline, str):
                deadline = datetime.fromisoformat(deadline)

            if deadline < datetime.now():
                return {'message': 'Deadline cannot be in the past'}, 400

            funding.deadline = deadline

        if status:
            funding.status = sanitize_input(status)

        #REPLACE requirements (if provided)
        if requirements_list is not None:
            # delete old
            Requirements.query.filter_by(funding_window_id=funding_window_id).delete()

            cleaned_requirements = [
                sanitize_input(r.strip())
                for r in requirements_list
                if isinstance(r, str) and r.strip()
            ]

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

        #REPLACE categories (if provided)
        if grant_categories_list is not None:
            # delete old
            Categories.query.filter_by(funding_window_id=funding_window_id).delete()

            cleaned_categories = [
                sanitize_input(c.strip())
                for c in grant_categories_list
                if isinstance(c, str) and c.strip()
            ]

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
            f'Employee:{user_id} updated funding window ID:{funding_window_id}'
        )

        return {
            'message': 'Funding window updated successfully',
            'application_id': funding_window_id
        }, 200

    except Exception as e:
        db.session.rollback()
        print(f'Edit Funding Window Error: {e}')

        return {
            'message': 'Failed to update funding window',
            'error': str(e)
        }, 500