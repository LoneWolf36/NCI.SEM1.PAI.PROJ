from pathlib import Path

import markdown
from weasyprint import HTML

ROOT = Path(__file__).resolve().parent

# List of journal files to convert
journals = [
    "JOURNAL_Mohammed_Faizan_Khan_25214501.md",
    "JOURNAL_Sakshi_Patil_24304166.md",
    "JOURNAL_Shaskank_Yadav_25118692.md",
    "JOURNAL_Chetan_Panchal_24244058.md"
]

# Convert each journal to PDF
for journal in journals:
    journal_path = ROOT / journal
    # Read the Markdown file
    with open(journal_path, 'r', encoding='utf-8') as f:
        md_text = f.read()
    
    # Convert Markdown to HTML
    html = markdown.markdown(
        md_text,
        extensions=["tables", "fenced_code", "nl2br"],
    )
    
    # Add basic styling
    styled_html = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 32px 36px;
                line-height: 1.55;
                font-size: 11pt;
            }}
            h1, h2, h3 {{
                color: #333;
                margin-bottom: 0.35em;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 16px 0;
                font-size: 10.5pt;
            }}
            th, td {{
                border: 1px solid #999;
                padding: 6px 8px;
                vertical-align: top;
            }}
            th {{
                background: #f2f2f2;
            }}
            p, li {{
                margin-top: 0.25em;
                margin-bottom: 0.25em;
            }}
        </style>
    </head>
    <body>
        {html}
    </body>
    </html>
    """
    
    # Convert HTML to PDF
    pdf_filename = journal.replace('.md', '.pdf')
    pdf_path = ROOT / pdf_filename
    HTML(string=styled_html).write_pdf(str(pdf_path))
    print(f"Converted {journal_path.name} to {pdf_path.name}")
