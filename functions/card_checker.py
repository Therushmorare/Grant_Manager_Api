import re

def validate_account_number(account_number: str):
    try:
        # Remove spaces or dashes
        account_number = re.sub(r"[\s-]", "", account_number)

        # Must be digits only
        if not account_number.isdigit():
            return {"valid": False, "message": "Account number must contain only digits"}

        # Length check (SA-friendly range)
        if len(account_number) < 6 or len(account_number) > 11:
            return {"valid": False, "message": "Invalid account number length"}

        return {"valid": True, "message": "Valid account number"}

    except Exception as e:
        return {"valid": False, "message": str(e)}
    
def branch_checker(branch_code: str):
    try:
        branch_code = re.sub(r"[\s-]", "", branch_code)

        # Must be digits only
        if not branch_code.isdigit():
            return {"valid": False, "message": "Branch code must contain only digits"}

        # SA branch codes are typically 6 digits
        if len(branch_code) != 6:
            return {"valid": False, "message": "Branch code must be 6 digits"}

        return {"valid": True, "message": "Valid branch code"}

    except Exception as e:
        return {"valid": False, "message": str(e)}