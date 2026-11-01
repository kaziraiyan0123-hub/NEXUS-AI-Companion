"""
NEXUS Markdown & Code Syntax Highlighting Engine
Converts Markdown to beautiful, minimalist, glassmorphism-styled HTML
with syntax-highlighted code blocks. Clean modern palette (no neon borders).
"""
import html
import re
import markdown
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer, TextLexer
from pygments.formatters import HtmlFormatter
from interface.themes import CharacterSkin

def format_code_block(code_text: str, language: str = "") -> str:
    """Highlights code using Pygments and wraps in a sleek dark card."""
    code_text = code_text.strip()
    try:
        if language:
            lexer = get_lexer_by_name(language.strip(), stripall=True)
        else:
            lexer = guess_lexer(code_text)
    except Exception:
        lexer = TextLexer()

    formatter = HtmlFormatter(nowrap=True, noclasses=False)
    highlighted = highlight(code_text, lexer, formatter)
    lang_display = language.upper() if language else "CODE"

    return f"""
    <div class="code-card">
        <div class="code-header">
            <span class="code-lang">{lang_display}</span>
        </div>
        <pre class="code-body"><code>{highlighted}</code></pre>
    </div>
    """

def markdown_to_html(md_text: str, skin: CharacterSkin = None) -> str:
    """Converts Markdown text to rich HTML styled with clean modern aesthetics."""
    if not md_text:
        return ""

    # Ensure code blocks are closed for streaming safety
    if md_text.count("```") % 2 == 1:
        md_text = md_text + "\n```"

    # Replace fenced code blocks before markdown processing to preserve styling
    code_blocks = []
    def code_replacer(match):
        lang = match.group(1) or ""
        code = match.group(2)
        idx = len(code_blocks)
        code_blocks.append(format_code_block(code, lang))
        return f"@@@CODE_BLOCK_{idx}@@@"

    fenced_pattern = re.compile(r"```([a-zA-Z0-9_\-\+]*)\n(.*?)```", re.DOTALL)
    processed_md = fenced_pattern.sub(code_replacer, md_text)

    # Standard Markdown conversion
    html_output = markdown.markdown(
        processed_md,
        extensions=["fenced_code", "tables", "nl2br"]
    )

    # Re-insert code blocks
    for idx, block in enumerate(code_blocks):
        html_output = html_output.replace(f"@@@CODE_BLOCK_{idx}@@@", block)

    # Get Pygments CSS rules
    pygments_css = HtmlFormatter().get_style_defs('.code-body')

    # Full styled HTML wrapper
    full_html = f"""
    <html>
    <head>
    <style>
        body {{
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, 'Inter', sans-serif;
            font-size: 13.5px;
            line-height: 1.55;
            color: #e2e8f0;
            margin: 0;
            padding: 0;
            background-color: transparent;
        }}
        p {{
            margin: 0 0 7px 0;
        }}
        p:last-child {{
            margin-bottom: 0;
        }}
        h1, h2, h3, h4 {{
            color: #f8fafc;
            margin: 10px 0 5px 0;
            font-weight: 600;
        }}
        h1 {{ font-size: 15.5px; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 4px; }}
        h2 {{ font-size: 14px; }}
        h3 {{ font-size: 13.5px; }}
        ul, ol {{
            margin: 4px 0 7px 18px;
            padding: 0;
        }}
        li {{
            margin-bottom: 3px;
        }}
        blockquote {{
            border-left: 3px solid #38bdf8;
            background: rgba(56, 189, 248, 0.05);
            margin: 6px 0;
            padding: 5px 12px;
            border-radius: 0 6px 6px 0;
            color: #cbd5e1;
        }}
        code {{
            font-family: 'Consolas', 'Cascadia Code', monospace;
            font-size: 12px;
            background: rgba(255, 255, 255, 0.07);
            border: 1px solid rgba(255, 255, 255, 0.08);
            color: #7dd3fc;
            padding: 1px 5px;
            border-radius: 4px;
        }}
        .code-card {{
            background: #090d16;
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 8px;
            margin: 7px 0;
            overflow: hidden;
        }}
        .code-header {{
            background: rgba(255, 255, 255, 0.03);
            border-bottom: 1px solid rgba(255, 255, 255, 0.06);
            padding: 4px 10px;
            display: flex;
            justify-content: space-between;
            font-size: 11px;
            color: #94a3b8;
            font-weight: 600;
        }}
        .code-lang {{
            color: #38bdf8;
            font-weight: 700;
            letter-spacing: 0.5px;
        }}
        .code-body {{
            font-family: 'Consolas', 'Cascadia Code', monospace;
            font-size: 12px;
            padding: 8px 10px;
            margin: 0;
            background: #070a10;
            overflow-x: auto;
            color: #e2e8f0;
            line-height: 1.45;
        }}
        a {{
            color: #38bdf8;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 7px 0;
            font-size: 12.5px;
        }}
        th, td {{
            border: 1px solid rgba(255, 255, 255, 0.08);
            padding: 5px 8px;
            text-align: left;
        }}
        th {{
            background: rgba(255, 255, 255, 0.04);
            color: #f1f5f9;
            font-weight: 600;
        }}
        /* Pygments Syntax Theme */
        {pygments_css}
    </style>
    </head>
    <body>
    {html_output}
    </body>
    </html>
    """
    return full_html
