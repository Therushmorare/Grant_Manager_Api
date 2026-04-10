from flask import Blueprint, request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_restx import reqparse
from werkzeug.datastructures import FileStorage
import json
from config import Config
from core.auth.user_signin import signin_users
from core.applicants.sign_up import applicant_signup
from core.applicants.create_account import applicant_profile
from core.applicants.contact_persons import add_contact_person
from core.applicants.banking_details import banking_details
from core.applicants.complaince import documents
from core.applicants.make_application import make_application

limiter = Limiter(get_remote_address, default_limits=["100 per hour"], storage_uri= Config.redis_connection)

"""
------------------------------------------------------------------------------------
MAIN ROUTES FOR APPLICANTS
------------------------------------------------------------------------------------
"""

applicants_ns = Namespace("applicants", description="Applicants API endpoints")

# -----------------------------
# Models
# -----------------------------

login_model_v2 = applicants_ns.model("LoginV2", {
    "email": fields.String(required=True),
    "password": fields.String(required=True),
    "user_type": fields.String(required=True, description="Type of user (e.g., candidate, admin)")
})

signup_model = applicants_ns.model("Signup", {
    "email": fields.String(required=True),
    "password": fields.String(required=True)
})

auth_model = applicants_ns.model("ErrorResponse", {
    "message": fields.String(
        description="Error message",
        example="Invalid credentials"
    )
})

signup_success_model = applicants_ns.model(
    "SignupSuccess",
    {
        "message": fields.String(example="Signed Up successfully")
    }
)

error_model = applicants_ns.model("ErrorResponse", {
    "message": fields.String(
        description="Error message",
        example="Something went wrong, please try again later"
    )
})

create_profile_model = applicants_ns("Create Profile", {
    "applicant_id": fields.String(required=True),
    "company_legal_name": fields.String(required=True),
    "trading_name": fields.String(required=True),
    "registration_number": fields.String(required=True),
    "company_type": fields.String(required=True),
    "industry": fields.String(required=True),
    "seta_affiliation": fields.String(required=True),
    "registered_address": fields.String(required=True),
    "physical_address": fields.String(required=True),
    "city": fields.String(required=True),
    "province": fields.String(required=True),
    "postal_code": fields.String(required=True),
    "country": fields.String(required=True)
})

create_profile_success_model = applicants_ns.model(
    "CreateProfileSuccess",
    {
        "message": fields.String(example=" Profile added successfully"),
        "applicant_id": fields.String,
        "company_legal_name": fields.String,
        "trading_name": fields.String,
        "registration_number": fields.Integer,
        "industry": fields.String,
        "seta_affiliation": fields.String,
        "registered_address": fields.String,
        "physical_address": fields.String,
        "city": fields.String,
        "province": fields.String,
        "postal_code": fields.Integer,
        "country": fields.String
    }
)

add_contact_person_model = applicants_ns("Add Contact Person",
    {
        "applicant_id": fields.String(required=True),
        "names_list": fields.List(
            fields.String,
            required=True,
            example=["John", "Flint"]
        ),
        "email_list": fields.List(
            fields.String,
            required=True,
            example=["john@mail.com", "flint@mail.com"]
        ),
        "phone_list": fields.List(
            fields.String,
            required=True,
            example=["+218765432211", "+215432219988"]
        ),
        "role_list": fields.List(
            fields.String,
            required=True,
            example=["CEO", "Manager"]
        )
    }
)

contact_person_success_model = applicants_ns.model(
    "ContactPersonSuccess",
    {
        "message": fields.String(example=" Contact person added successfully"),
        "applicant_id": fields.String,
        "names_list": fields.List(fields.String),
        "email_list": fields.List(fields.String),
        "phone_list": fields.List(fields.String),
        "role_list": fields.List(fields.String)
    }
)

add_banking_details_model = applicants_ns(
    "Add Banking Details",
    {
        "applicant_id": fields.String(required=True),
        "bank_name": fields.String(required=True),
        "account_holder": fields.String(required=True),
        "account_number": fields.String(required=True),
        "branch_code": fields.String(required=True),
        "account_type": fields.String(required=True)
    }
)

banking_details_success_model = applicants_ns.model(
    "BankingDetailsSuccess",
    {
        "message": fields.String(example="Banking details added successfully"),
        "applicant_id": fields.String,
        "bank_name": fields.String,
        "account_holder": fields.String,
        "account_number": fields.String,
        "branch_code": fields.String,
        "account_type": fields.String
    }
)

document_success_model = applicants_ns.model("DocumentSuccess", {
    "message": fields.String(example="Document uploaded successfully"),
    "applicant_id": fields.String,
    "doc_type": fields.String(example="[CIPC_Registration, Tax_Clearance, Bank_Confirmation_Letter, Proof_of_Address, Accreditation_Certificate]"),
    "document": fields.String(example="CIPC.pdf")
})

application_success_model = applicants_ns.model("ApplicationSuccess", {
    "message": fields.String(example="Application created successfully"),
    "applicant_id": fields.String,
    "funding_window_id": fields.String,
    "programme_title": fields.String,
    "programme_decription": fields.String,
    "category": fields.String,
    "type": fields.String,
    "required_funding": fields.String,
    "number_of_learners": fields.String,
    "start_date": fields.String,
    "end_date": fields.String,
    "proposal_doc": fields.String(example="CIPC.pdf")
})

# -----------------------------
# Endpoints
# -----------------------------
@applicants_ns.route("/login")
class ApplicantLogin(Resource):
    @applicants_ns.expect(login_model_v2, validate=True)
    @limiter.limit("10 per minute")
    # @jwt_required()
    def post(self):
        data = request.json
        result, status = signin_users(data.get("email"), data.get("password"), data.get("user_type"))
        return result, status


@applicants_ns.route("/signup")
class ApplicantSignup(Resource):
    @applicants_ns.doc(
        description="Applicant signs up.",
        responses={
            200: ("Administrator added successfully", signup_success_model),
            400: ("Validation error – missing fields", error_model),
            409: ("Duplicate email or employee number", error_model),
            500: ("Internal server error", error_model)
        }
    )
    @applicants_ns.expect(signup_model, validate=True)
    @limiter.limit("10 per minute")
    # @jwt_required()
    def post(self):
        data = request.json
        result, status = applicant_signup(data.get("email"), data.get("password"))
        return result, status
    
@applicants_ns.route("/createProfile")
class ApplicantCreateProfile(Resource):
    @applicants_ns.doc(
        description="Applicant create profile.",
        responses={
            200:("Profile creacted successfully", create_profile_success_model),
            400: ("Validation error – missing fields", error_model),
            409: ("Duplicate email or employee number", error_model),
            500: ("Internal server error", error_model)

        }
    )
    @applicants_ns.expect(create_profile_model, validate=True)
    @limiter.limit("10 per minute")
    # @jwt_required()
    def post(self):
        data = request.json
        result, status = applicant_profile(
            data.get("applicant_id"),
            data.get("company_legal_name"),
            data.get("trading_name"),
            data.get("registration_number"),
            data.get("company_type"),
            data.get("industry"),
            data.get("seta_affiliation"),
            data.get("registered_address"),
            data.get("physical_address"),
            data.get("city"),
            data.get("province"),
            data.get("postal_code"),
            data.get("country")
        )
        return result, status

@applicants_ns.route("/addContactPerson")
class AddContactPerson(Resource):
    @applicants_ns.doc(
        description="Add contact person.",
        responses={
            200: ("Contact person added successfully", contact_person_success_model),
            400: ("Validation error – missing fields", error_model),
            409: ("Duplicate email or employee number", error_model),
            500: ("Internal server error", error_model)
        }
    )
    @applicants_ns.expect(add_contact_person_model, validate=True)
    @limiter.limit("10 per minute")
    # @jwt_required()
    def post(self):
        data = request.json
        payload = request.get_json()

        result, status = add_contact_person(
            applicant_id=payload.get('applicant_id'),
            names_list=payload.get("names_list"),
            emails_list=payload.get("emails_list"),
            phone_list=payload.get("phone_list"),
            role_list=payload.get('role_list')
        )
        return result, status

@applicants_ns.route("/addBankingDetails")
class AddBankingDetails(Resource):
    @applicants_ns.doc(
        description="Add banking details.",
        responses={
            200: ("Banking details added successfully", banking_details_success_model),
            400: ("Validation error – missing fields", error_model),
            409: ("Duplicate email or employee number", error_model),
            500: ("Internal server error", error_model)
        }
    )
    @applicants_ns.expect(add_banking_details_model, validate=True)
    @limiter.limit("10 per minute")
    # @jwt_required()
    def post(self):
        data = request.json
        payload = request.get_json()

        result, status = banking_details(
            applicant_id=payload.get('applicant_id'),
            bank_name=payload.get("bank_name"),
            account_holder=payload.get("account_holder"),
            account_number=payload.get("account_number"),
            branch_code=payload.get('branch_code'),
            account_type=payload.get("account_type")
        )
        return result, status

@applicants_ns.route("/addDocuments")
class AddDocuments(Resource):

    @applicants_ns.doc(
        description="Upload a new document.",
        params={
            "applicant_id":{
                "description": "Applicant ID",
                "in": "formData",
                "type": "string",
                "required": True
            },
            "doc_type": {
                "description": "Type of document uploaded",
                "in": "formData",
                "type": "string",
                "required": True
            },

            "document": {
                "description": "Document file (PDF, DOCX)",
                "in": "formData",
                "type": "file",
                "required": True
            }
        },
        responses={
            200: ("Document added successfully", document_success_model),
            400: ("Validation error", error_model),
            404: ("Document already exists", error_model),
            500: ("Internal server error", error_model)
        }
    )
    @limiter.limit("5/minute")
    # @jwt_required()
    def post(self):
        """
        Add Documents
        ------------------
        """
        applicant_id = request.form.get("applicant_id")
        doc_type = request.form.get("doc_type")
        document = request.files.get("document")

        result, status_code = documents(
            applicant_id=applicant_id,
            doc_type=doc_type,
            document=document,
        )

        return result, status_code

@applicants_ns.route("/makeApplication")
class MakeApplication(Resource):

    @applicants_ns.doc(
        description="Make a new funding application.",
        params={
            "applicant_id":{
                "description": "Applicant ID",
                "in": "formData",
                "type": "string",
                "required": True
            },
            "funding_window_id":{
                "description": "Funding Window ID",
                "in": "formData",
                "type": "string",
                "required": True
            },

            "programme_title": {
                "description": " Programme title",
                "in": "formData",
                "type": "string",
                "required": True
            },
            "programme_description": {
                "description": " Programme description",
                "in": "formData",
                "type": "Text",
                "required": True
            },
            "category": {
                "description": "programme categories",
                "in": "formData",
                "type": "string",
                "required": True
            },

            "type": {
                "description": " Programme type",
                "in": "formData",
                "type": "string",
                "required": True
            },
            "required_funding": {
                "description": " How much is required to run the programme",
                "in": "formData",
                "type": "Float",
                "required": True
            },
            "number_of_learners": {
                "description": " Number of students required",
                "in": "formData",
                "type": "Integer",
                "required": True
            },
            "start_date": {
                "description": " Programme start date",
                "in": "formData",
                "type": "string",
                "required": True
            },
            "end_date": {
                "description": " Programme end date",
                "in": "formData",
                "type": "string",
                "required": True
            },
            "proposal_doc": {
                "description": "Document file (PDF, DOCX)",
                "in": "formData",
                "type": "file",
                "required": True
            }
        },
        responses={
            200: ("Document added successfully", application_success_model),
            400: ("Validation error", error_model),
            404: ("Document already exists", error_model),
            500: ("Internal server error", error_model)
        }
    )
    @limiter.limit("5/minute")
    # @jwt_required()
    def post(self):
        """
        Make Funding Application
        ------------------
        """
        applicant_id = request.form.get("applicant_id")
        funding_window_id = request.form.get("funding_window_id")
        programme_title = request.form.get("programme_title")
        programme_decription = request.form.get("programme_decription")
        category = request.form.get("category")
        type = request.form.get("type")
        required_funding = request.form.get("required_funding")
        number_of_learners = request.form.get("number_of_learners")
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")
        proposal_doc = request.files.get("proposal_doc")

        result, status_code = make_application(
            applicant_id=applicant_id,
            funding_window_id=funding_window_id,
            programme_title=programme_title,
            programme_decription=programme_decription,
            category=category,
            type=type,
            required_funding=required_funding,
            number_of_learners=number_of_learners,
            start_date=start_date,
            end_date=end_date,
            proposal_doc=proposal_doc
        )

        return result, status_code

@applicants_ns.route("/editProfile")
class EditProfile(Resource):
    @applicants_ns.doc(
        description="Applicant edit's profile.",
        responses={
            200:("Profile creacted successfully", create_profile_success_model),
            400: ("Validation error – missing fields", error_model),
            409: ("Duplicate email or employee number", error_model),
            500: ("Internal server error", error_model)

        }
    )
    @limiter.limit("10/minute")
    # @jwt_required()
    def post(self):
        """
        Make Funding Application
        ------------------
        """
        data = request.json
        result, status = applicant_profile(
            data.get("applicant_id"),
            data.get("company_legal_name"),
            data.get("trading_name"),
            data.get("registration_number"),
            data.get("company_type"),
            data.get("industry"),
            data.get("seta_affiliation"),
            data.get("registered_address"),
            data.get("physical_address"),
            data.get("city"),
            data.get("province"),
            data.get("postal_code"),
            data.get("country")
        )
        return result, status

@applicants_ns.route("/editContactPerson")
class EditContactPerson(Resource):
    @applicants_ns.doc(
        description="Edit contact person.",
        responses={
            200: ("Contact person added successfully", contact_person_success_model),
            400: ("Validation error – missing fields", error_model),
            409: ("Duplicate email or employee number", error_model),
            500: ("Internal server error", error_model)
        }
    )
    @applicants_ns.expect(add_contact_person_model, validate=True)
    @limiter.limit("10 per minute")
    # @jwt_required()
    def post(self):
        data = request.json
        payload = request.get_json()

        result, status = add_contact_person(
            applicant_id=payload.get('applicant_id'),
            names_list=payload.get("names_list"),
            emails_list=payload.get("emails_list"),
            phone_list=payload.get("phone_list"),
            role_list=payload.get('role_list')
        )
        return result, status
