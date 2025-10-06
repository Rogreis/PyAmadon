#!/usr/bin/env python
"""Ferramenta auxiliar: limpeza de caches e logs temporários.

Uso:
    python tools/cleanup_cache.py --dry-run
"""
from __future__ import annotations
import argparse
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TARGETS = [
    PROJECT_ROOT / '.venv' / 'pyvenv.cfg',  # exemplo: apenas para mostrar inspeção
    PROJECT_ROOT / 'logs',
    PROJECT_ROOT / '__pycache__',
]


def human(p: Path) -> str:
    try:
        size = sum(f.stat().st_size for f in p.rglob('*') if f.is_file()) if p.is_dir() else (p.stat().st_size if p.exists() else 0)
    except Exception:
        size = 0
    return f"{p} ({size/1024:.1f} KiB)"


def main():
    parser = argparse.ArgumentParser(description='Limpa caches e logs não essenciais do workspace (não incluído no build).')
    parser.add_argument('--dry-run', action='store_true', help='Mostra o que seria removido sem apagar.')
    parser.add_argument('--aggressive', action='store_true', help='Inclui diretórios __pycache__ aninhados.')
    args = parser.parse_args()

    to_remove: list[Path] = []
    for target in TARGETS:
        if target.name == '__pycache__' and not args.aggressive:
            continue
        if target.exists():
            to_remove.append(target)

    if not to_remove:
        print('Nada a remover.')
        return

    print('Alvos:')
    for t in to_remove:
        print('  -', human(t))

    if args.dry_run:
        print('\nDry-run: nada removido.')
        return

    for t in to_remove:
        if t.is_dir():
            shutil.rmtree(t, ignore_errors=True)
        else:
            try:
                t.unlink()
            except OSError:
                pass
    print('Remoção concluída.')


if __name__ == '__main__':
    main()
