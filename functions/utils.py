import re


def replace_variables(text, data):
    """
    Replaces {{variable}} in text with values from data
    """

    def replacer(match):
        key = match.group(1)
        return str(data.get(key, f"{{{{{key}}}}}"))

    return re.sub(r"\{\{(.*?)\}\}", replacer, text)