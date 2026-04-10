#!/usr/bin/python3
from redis_config import redis_client
from flask import jsonify, request
from sqlalchemy import desc
from sqlalchemy import func, case
from sqlalchemy.orm import joinedload
from datetime import datetime, timezone
from math import ceil
from functions.celery_worker import celery_ext
from functions.date_formater import format_date
from functions.date_parser import parse_date_flexibly, safe_date
from database import db
from functions.date_formater import format_date
from functions.date_parser import parse_date_flexibly, safe_date
from datetime import datetime
from models.applicant import Applicant
from models.applicant_profile import ApplicantProfile
from models.contact_person import ContactPersons

#get applicants data
@celery_ext.celery.task
def get_all_applicants():
    try:
        applicants = Applicant.query.all()

        if not applicants:
            return {'message': 'Applicants do not exist'}, 404
        
        result = [
            {
            'admin_id': applicant.id,
            'email': applicant.email,
            'status': applicant.status,
            'is_verified': applicant.is_verified,
            'is_active': applicant.is_active,
            'created_at': applicant.created_at.isoformat() if admin.created_at else None,
            }
            for applicant in applicants
        ]
        return result, 200
    
    except Exception as e:
        print(f"Get all Applicants error:{e}")
        return {'message': 'Something went wrong'}, 500

#get applicant profile
@celery_ext.celery.task
def get_applicants_profile():
    try:
        profiles = ApplicantProfile.query.all()

        if not profiles:
            return {'message': 'Applicant profiles do not exists'}, 404
        
        result = [
            {
                'profile_id': profile.profile_id,
                'applicant_id': profile.applicant_id,
                'legal_name': profile.legal_name,
                'trading_name': profile.trading_name,
                'registration_number': profile.registration_number,
                'company_type': profile.company_type,
                'industry': profile.industry,
                'seta_affiliation': profile.seta_affiliation,
                'registered_address': profile.registered_address,
                'physical_address': profile.physical_address,
                'city': profile.city,
                'province': profile.province,
                'postal_code': profile.postal_code,
                'country': profile.country,
                'verification_status': profile.verification_status,
                'is_verified': profile.is_verified,
                'verified_by': profile.verified_by,
                'created_at': profile.created_at.isoformat() if profile.created_at else None
            }
            for profile in profiles
        ]
        return result, 200
    
    except Exception as e:
        print(f"Get all profiles error:{e}")
        return {'message': 'Something went wrong'}, 500
    

#get all contact persons
def get_contact_persons(id):
    try:
        contact_persons = ContactPersons.query.filter_by(applicant_id=id).first()

        if not contact_persons:
            return {'message': 'Contact persons dont exist'}, 404
        
        result = {
            'applicant_id': contact_persons.applicant_id,
            'contact_id': contact_persons.contract_id,
            'name': contact_persons.name,
            'email': contact_persons.email,
            'phone': contact_persons.phone,
            'role': contact_persons.role
        }
        return result, 200
    
    except Exception as e:
        print(f"Get all contact persons error:{e}")
        return {'message': 'Something went wrong'}, 500
