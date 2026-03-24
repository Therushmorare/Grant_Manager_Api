from database import db
from models.contract import Contract
from core.contract_engine.generate_contract import generate_contract, render_to_html
from functions.pdf_gen import generate_pdf_from_html

class ContractService:

    def __init__(self, application_id, template_id, schema, data):
        self.application_id = application_id
        self.template_id = template_id
        self.schema = schema
        self.data = data

        self.sections = None
        self.html = None
        self.contract = None

    # -------- BUILD --------
    def build(self):
        self.sections = generate_contract(self.schema, self.data)
        self.html = render_to_html(self.sections)
        return self

    # -------- SAVE --------
    def save(self):
        if not self.sections or not self.html:
            raise Exception("Contract not built")

        self.contract = Contract(
            application_id=self.application_id,
            template_id=self.template_id,
            content=self.sections,
            html=self.html
        )

        db.session.add(self.contract)
        db.session.commit()

        return self

    # -------- EXPORT PDF --------
    def export_pdf(self):
        if not self.html:
            raise Exception("Contract not built")

        return generate_pdf_from_html(self.html)

    # -------- LOAD --------
    @staticmethod
    def load(contract_id):
        contract = Contract.query.get(contract_id)

        if not contract:
            raise Exception("Contract not found")

        service = ContractService(
            contract.application_id,
            contract.template_id,
            {},
            {}
        )

        service.sections = contract.content
        service.html = contract.html
        service.contract = contract

        return service