def check_domain(email_address, allowed_domains):
    try:
        domain = email_address.split('@')[1]
        if domain in allowed_domains:
            return True, f"Domain '{domain}' is not allowed."
    except IndexError:
        return False, "Invalid email format."
