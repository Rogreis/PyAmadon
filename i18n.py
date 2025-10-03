"""Carregamento simples de recursos de texto (i18n) para a aplicação Amadon.

Este módulo oferece:
- load_locale(locale): carrega o arquivo JSON de mensagens para o locale especificado.
- translate(key, **kwargs): retorna a string localizada com formatação opcional.
- Alias _ = translate para uso conciso.

Formato do arquivo de recursos (JSON):
{
  "app.title": "Título...",
  "alguma.chave": "Texto com {placeholders}"
}

Se a chave não existir, retorna a própria chave entre < > para facilitar identificação.
"""
from __future__ import annotations

from pathlib import Path
import json
from typing import Dict, Any

_BASE_DIR = Path(__file__).parent / "resources"
_loaded_messages: Dict[str, Dict[str, str]] = {}
_current_locale: str = "pt_BR"


def load_locale(locale: str = "pt_BR") -> None:
    global _current_locale
    if locale in _loaded_messages:
        _current_locale = locale
        return
    file_path = _BASE_DIR / f"messages_{locale}.json"
    if not file_path.exists():
        raise FileNotFoundError(f"Arquivo de mensagens não encontrado: {file_path}")
    with file_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):  # pragma: no cover
        raise ValueError("O arquivo de mensagens deve conter um objeto JSON")
    _loaded_messages[locale] = {str(k): str(v) for k, v in data.items()}
    _current_locale = locale


def translate(key: str, **kwargs: Any) -> str:
    msgs = _loaded_messages.get(_current_locale, {})
    raw = msgs.get(key)
    if raw is None:
        return f"<{key}>"
    if kwargs:
        try:
            return raw.format(**kwargs)
        except Exception:  # pragma: no cover - fallback em erro de formatação
            return raw
    return raw

# Alias comum estilo gettext
_ = translate

# Carrega locale padrão ao importar
try:  # pragma: no cover
    load_locale(_current_locale)
except Exception:
    pass
