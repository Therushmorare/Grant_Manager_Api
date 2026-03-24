def calculate_compliance_score(applicant_id, application):
    profile = ApplicantProfile.query.filter_by(applicant_id=applicant_id).first()
    contacts = ContactPersons.query.filter_by(applicant_id=applicant_id).all()
    docs = ApplicantDocuments.query.filter_by(applicant_id=applicant_id).all()
    banking = BankAccounts.query.filter_by(applicant_id=applicant_id).first()

    score = 0

    # Profile (20)
    if profile:
        if profile.legal_name: score += 5
        if profile.registration_number: score += 5
        if profile.industry: score += 5
        if profile.seta_affiliation: score += 5

    # Contacts (10)
    if contacts:
        score += 10

    # Documents (30)
    required_docs = ['CIPC_Registration', 'Tax_Clearance', 'Bank_Confirmation_Letter']

    for doc_type in required_docs:
        for doc in docs:
            if doc.type == doc_type and doc.verification_status == 'VERIFIED':
                score += 10
                break

    # Banking (20)
    if banking and banking.is_verified:
        score += 20

    # Quality (20)
    if application.cost_per_learner < 10000:
        score += 10
    elif application.cost_per_learner < 20000:
        score += 5

    if 30 <= application.duration <= 365:
        score += 10

    return score