from core.auth.account_checker import account_checker
from models.applicant_profile import ApplicantProfile
from models.visit import SiteVisit
from models.inspection import Inspection

def generate_site_report(applicant_id, visit_id):
    try:
        # Validate applicant
        if not account_checker(applicant_id):
            return {'message': 'Applicant does not exist'}, 404

        # Get applicant profile
        profile = ApplicantProfile.query.filter_by(applicant_id=applicant_id).first()
        if not profile:
            return {'message': 'Applicant profile does not exist'}, 404

        # Get site visit
        visit = SiteVisit.query.filter_by(visit_id=visit_id).first()
        if not visit:
            return {'message': 'Site visit does not exist'}, 404

        # Get all inspections for this visit
        inspections = Inspection.query.filter_by(visit_id=visit_id).all()
        if not inspections:
            return {'message': 'No inspections found for this visit'}, 404

        # Generate summary
        passed_count = sum(1 for i in inspections if i.status == 'PASSES')
        failed_count = sum(1 for i in inspections if i.status == 'FAILED')
        total_inspections = len(inspections)

        summary = (
            f"This site visit report covers the inspection conducted on {visit.date} at "
            f"{visit.location}. A total of {total_inspections} inspections were performed, "
            f"with {passed_count} passing and {failed_count} failing."
        )

        # Build table of contents
        table_of_contents = [
            "1. Applicant Information",
            "2. Site Visit Details",
            "3. Inspections Summary",
            "4. Detailed Inspections"
        ]

        # Build report
        report = {
            'title': f"Site Visit Report - {visit.visit_id}",
            'summary': summary,
            'table_of_contents': table_of_contents,
            'sections': {
                'applicant_info': {
                    'name': profile.full_name,
                    'email': profile.email,
                    'phone': profile.phone_number,
                    'company': getattr(profile, 'company_name', None)
                },
                'visit_info': {
                    'visit_id': visit.visit_id,
                    'date': str(visit.date),
                    'time': str(visit.time),
                    'location': visit.location,
                    'status': visit.status,
                    'assigned_to': visit.assigned_to
                },
                'inspections_summary': {
                    'total': total_inspections,
                    'passed': passed_count,
                    'failed': failed_count
                },
                'detailed_inspections': []
            }
        }

        # Add detailed inspections
        for idx, ins in enumerate(inspections, start=1):
            report['sections']['detailed_inspections'].append({
                'inspection_number': idx,
                'inspection_id': ins.id,
                'monitor_id': ins.monitor_id,
                'status': ins.status,
                'comments': ins.comments,
                'evidence_files': [ins.file]  # If multiple files, you can expand to list all
            })

        return {
            'message': 'Site visit report generated successfully',
            'report': report
        }, 200

    except Exception as e:
        print(f'Site report generation error: {e}')
        return {'message': 'Something went wrong'}, 500