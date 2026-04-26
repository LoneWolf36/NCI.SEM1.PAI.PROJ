from pathlib import Path

import markdown
from weasyprint import HTML


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "FINAL_REPORT.md"
HTML_OUT = ROOT / "FINAL_REPORT.html"
PDF_OUT = ROOT / "FINAL_REPORT.pdf"


def build_html(markdown_text: str) -> str:
    body = markdown.markdown(
        markdown_text,
        extensions=["tables", "fenced_code", "nl2br", "sane_lists"],
    )
    return f"""
    <html>
    <head>
        <meta charset="utf-8" />
        <style>
            @page {{
                size: A4;
                margin: 18mm 15mm 18mm 15mm;
            }}
            body {{
                font-family: "Times New Roman", serif;
                font-size: 10pt;
                line-height: 1.35;
                color: #111;
            }}
            h1 {{
                font-size: 18pt;
                margin-bottom: 0.2em;
                text-align: center;
            }}
            h2 {{
                font-size: 12pt;
                border-bottom: 1px solid #444;
                margin-top: 1.2em;
                margin-bottom: 0.4em;
                padding-bottom: 0.15em;
            }}
            h3 {{
                font-size: 10.5pt;
                margin-top: 0.9em;
                margin-bottom: 0.2em;
            }}
            p {{
                text-align: justify;
                margin: 0.3em 0;
            }}
            ul, ol {{
                margin-top: 0.25em;
                margin-bottom: 0.45em;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 10px 0 14px 0;
                font-size: 9pt;
            }}
            th, td {{
                border: 1px solid #555;
                padding: 4px 6px;
                vertical-align: top;
            }}
            th {{
                background: #efefef;
            }}
            img {{
                max-width: 100%;
                display: block;
                margin: 10px auto;
            }}
            code {{
                font-size: 9pt;
            }}
            hr {{
                border: 0;
                border-top: 1px solid #888;
                margin: 12px 0;
            }}
        </style>
    </head>
    <body>
        {body}
    </body>
    </html>
    """


def main() -> None:
    markdown_text = SOURCE.read_text(encoding="utf-8")
    html = build_html(markdown_text)
    HTML_OUT.write_text(html, encoding="utf-8")
    HTML(string=html, base_url=str(ROOT)).write_pdf(str(PDF_OUT))
    print(f"Wrote {HTML_OUT.name}")
    print(f"Wrote {PDF_OUT.name}")


if __name__ == "__main__":
    main()
