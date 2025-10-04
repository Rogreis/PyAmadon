"""Validador de estrutura de documentos e âncoras.

Uso:
    python validate_docs.py

Verifica:
1. Se todos os links em assets/data/documentos_tree.json possuem arquivo existente.
2. Se a âncora (fragmento #...) existe no HTML final (HTML direto ou Markdown convertido parcialmente).
3. Relatório consolidado com contagens e detalhes de falhas.

Limitações:
- Para Markdown, procura literalmente pelo padrão id="..." após conversão manual leve: aqui apenas leitura do texto bruto (se id inserido via <hX id="...">). Caso id não esteja explicitamente no markdown (ex: título puro), não será encontrado.

Extensões futuras:
- Usar markdown2 para converter e então buscar a âncora no HTML convertido.
- Validar unicidade de IDs.
- Gerar sugestão de próximas âncoras disponíveis.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
DATA_JSON = ROOT / "assets" / "data" / "documentos_tree.json"
DOCS_DIR = ROOT / "assets" / "docs"

LINK_RE = re.compile(r"^doc://(?P<file>Doc\d+\.html)(?:#(?P<anchor>p\d{3}_\d{3}_\d{3}))?$")
ID_RE = re.compile(r'id=["\'](?P<id>p\d{3}_\d{3}_\d{3})(?:_[0-9A-Za-z]+)?["\']')

class Issue:
    def __init__(self, level: str, message: str, link: str):
        self.level = level
        self.message = message
        self.link = link
    def __str__(self):
        return f"[{self.level}] {self.link} -> {self.message}"


def iter_links(node):
    yield node.get("titulo"), node.get("link")
    for filho in node.get("filhos", []) or []:
        yield from iter_links(filho)


def load_tree():
    with DATA_JSON.open("r", encoding="utf-8") as f:
        data = json.load(f)
    for n in data.get("nodes", []):
        yield from iter_links(n)


def validate():
    issues: list[Issue] = []
    total = 0
    ok = 0
    anchors_found_cache: dict[Path, set[str]] = {}

    for titulo, link in load_tree():
        if not link:
            issues.append(Issue("ERROR", "Link vazio", f"{titulo}"))
            continue
        total += 1
        m = LINK_RE.match(link)
        if not m:
            issues.append(Issue("ERROR", "Formato inválido", link))
            continue
        file_html = m.group("file")
        anchor = m.group("anchor")
        # Arquivo pode ser .html ou .md fisicamente
        base_name = file_html[:-5]  # remove .html
        physical_html = DOCS_DIR / f"{base_name}.html"
        physical_md = DOCS_DIR / f"{base_name}.md"
        phys_path: Path | None = None
        if physical_html.exists():
            phys_path = physical_html
        elif physical_md.exists():
            phys_path = physical_md
        if phys_path is None:
            issues.append(Issue("ERROR", "Arquivo não encontrado", link))
            continue
        # Carrega IDs só uma vez por arquivo
        if phys_path not in anchors_found_cache:
            try:
                text = phys_path.read_text(encoding="utf-8", errors="ignore")
            except Exception as e:  # pragma: no cover
                issues.append(Issue("ERROR", f"Falha leitura: {e}", link))
                continue
            anchors_found_cache[phys_path] = set(ID_RE.findall(text))
        if anchor:
            if anchor in anchors_found_cache[phys_path]:
                ok += 1
            else:
                issues.append(Issue("WARN", "Âncora não encontrada no arquivo", link))
        else:
            ok += 1
    return total, ok, issues


def main():
    total, ok, issues = validate()
    errors = [i for i in issues if i.level == "ERROR"]
    warns = [i for i in issues if i.level == "WARN"]
    print("Resumo Validação:")
    print(f"  Total links: {total}")
    print(f"  OK: {ok}")
    print(f"  Errors: {len(errors)}  Warnings: {len(warns)}")
    if errors:
        print("\nErros:")
        for e in errors:
            print(" -", e)
    if warns:
        print("\nAvisos:")
        for w in warns:
            print(" -", w)
    if not errors:
        print("\nStatus geral: PASS (sem erros críticos)")
    else:
        print("\nStatus geral: FAIL (há erros)")

if __name__ == "__main__":  # pragma: no cover
    main()
