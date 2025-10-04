from pathlib import Path
from typing import Tuple

try:  # optional dependency
    import markdown2  # type: ignore
except Exception:  # pragma: no cover
    markdown2 = None  # type: ignore

CONTENT_ROOT = Path('assets') / 'docs'


def parse_logical_link(link: str) -> Tuple[str | None, str | None]:
    """Parses logical link patterns.

    Expected formats:
      doc://Doc000.html#anchor_id
      doc://Doc000.html
    Returns (filename, anchor)
    """
    if not link.startswith('doc://'):
        return None, None
    raw = link[len('doc://'):]
    if '#' in raw:
        fname, anchor = raw.split('#', 1)
    else:
        fname, anchor = raw, None
    return fname or None, anchor or None


def load_document_html(filename: str) -> str | None:
    """Loads HTML or Markdown into HTML.

    Search order:
      1. assets/docs/<filename> (if already .html)
      2. assets/docs/<stem>.md (if HTML not present)
    """
    path = CONTENT_ROOT / filename
    if path.suffix.lower() != '.html':
        # force .html expectation, but allow fallback to md
        html_path = CONTENT_ROOT / (Path(filename).stem + '.html')
    else:
        html_path = path
    if html_path.exists():
        try:
            return html_path.read_text(encoding='utf-8')
        except Exception:
            return None
    # fallback markdown
    md_path = CONTENT_ROOT / (Path(filename).stem + '.md')
    if md_path.exists():
        try:
            text = md_path.read_text(encoding='utf-8')
            if markdown2:
                return markdown2.markdown(text, extras=["fenced-code-blocks", "tables", "strike", "footnotes"])  # type: ignore
            # minimal fallback: wrap paragraphs
            paras = '\n'.join(f'<p>{p}</p>' for p in text.splitlines() if p.strip())
            return f"<div class='md-fallback'>{paras}</div>"
        except Exception:
            return None
    return None


def build_final_body(html_fragment: str, anchor: str | None) -> str:
    """Wraps loaded HTML in a container and optionally scrolls to anchor via JS."""
    scroll_js = """<script>document.addEventListener('DOMContentLoaded',()=>{const a=document.getElementById('%s');if(a){a.scrollIntoView({behavior:'smooth',block:'start'});a.classList.add('__focus-anchor');}});</script>""" % anchor if anchor else ""
    style = """<style>.__focus-anchor{outline:2px solid #ff9800;transition:outline 1s ease;} body{padding:1rem;} pre{background:#222;padding:8px;border-radius:4px;color:#eee;} code{background:#eee;padding:2px 4px;border-radius:3px;} </style>"""
    return f"<div class='doc-container'>{html_fragment}</div>{scroll_js}{style}"


def resolve_doc_link(link: str) -> str:
    """Resolves a logical doc:// link into HTML body.

    Returns an informative HTML fragment if not found.
    """
    filename, anchor = parse_logical_link(link)
    if not filename:
        return f"<div class='alert alert-warning'>Link inválido: {link}</div>"
    content = load_document_html(filename)
    if not content:
        return f"<div class='alert alert-danger'>Conteúdo não encontrado para <code>{filename}</code>.</div>"
    return build_final_body(content, anchor)
