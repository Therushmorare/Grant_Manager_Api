from functions.utils import replace_variables


def generate_contract(contract_schema, data):
    rendered_sections = []

    for section in contract_schema.get("sections", []):

        section_type = section.get("type")

        if section_type not in {"logo", "header", "paragraph", "field", "clause", "signature"}:
            continue  # or raise error (better in production)

        rendered_sections.append(_build_section(section, data))

    return rendered_sections


def _build_section(section, data):
    section_type = section.get("type")

    if section_type == "logo":
        return {
            "type": "logo",
            "url": section.get("url")
        }

    if section_type == "header":
        return {
            "type": "header",
            "content": section.get("content", "")
        }

    if section_type == "paragraph":
        return {
            "type": "paragraph",
            "content": replace_variables(section.get("content", ""), data)
        }

    if section_type == "field":
        return {
            "type": "field",
            "label": section.get("label"),
            "value": data.get(section.get("key"), "")
        }

    if section_type == "clause":
        return {
            "type": "clause",
            "title": section.get("title"),
            "content": replace_variables(section.get("content", ""), data)
        }

    if section_type == "signature":
        return {"type": "signature"}