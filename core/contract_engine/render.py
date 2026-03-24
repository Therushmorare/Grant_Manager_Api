def render_to_html(sections):
    html_parts = []

    html_parts.append("""
    <html>
    <head>
        <style>
            body { font-family: Arial; padding: 40px; }
            h1 { text-align: center; }
            .clause { margin: 15px 0; }
            .logo img { height: 80px; }
        </style>
    </head>
    <body>
    """)

    for section in sections:

        section_type = section["type"]

        if section_type == "logo":
            html_parts.append(
                f"<div class='logo'><img src='{section['url']}' /></div>"
            )

        elif section_type == "header":
            html_parts.append(f"<h1>{section['content']}</h1>")

        elif section_type == "paragraph":
            html_parts.append(f"<p>{section['content']}</p>")

        elif section_type == "field":
            html_parts.append(
                f"<p><strong>{section['label']}:</strong> {section['value']}</p>"
            )

        elif section_type == "clause":
            html_parts.append(f"""
            <div class='clause'>
                <strong>{section['title']}</strong><br>
                {section['content']}
            </div>
            """)

        elif section_type == "signature":
            html_parts.append("<p>_____________________<br>Signature</p>")

    html_parts.append("</body></html>")

    return "".join(html_parts)