import re

def validate_cipc(reg_number):
    pattern = r"^\d{4}/\d{6}/\d{2}$"
    return bool(re.match(pattern, reg_number))