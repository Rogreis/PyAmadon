import sys
import logging
import threading
import time
from pathlib import Path
from PySide6.QtWidgets import QApplication

from mensagens import AmadonLogging, MensagensStatus
from main_window import main, main_window
from app_settings import apply_global_theme, settings
import urllib.request
import json
from i18n import _

RAW_URL = "https://github.com/Rogreis/TUB_Files/raw/refs/heads/main/AvailableTranslations.json"
DOWNLOADS_DIR = Path('downloads')
TRANSL_FILE = DOWNLOADS_DIR / 'AvailableTranslations.json'
ERR_FILE = DOWNLOADS_DIR / 'AvailableTranslations.err'

def _background_download_translations():
    """Efetua download em background do AvailableTranslations.json.

    Requisitos do usuário:
    - Se existir antes: já foi removido antes de iniciar (feito em run()).
    - Baixar silenciosamente; em caso de erro criar AvailableTranslations.err.
    - Não bloquear UI.
    """
    try:
        # Remove arquivo de erro anterior; somente interessa o resultado desta tentativa
        if ERR_FILE.exists():
            try:
                ERR_FILE.unlink()
            except Exception:
                pass
        DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
        tmp = TRANSL_FILE.with_suffix('.tmp')
        start = time.time()
        with urllib.request.urlopen(RAW_URL, timeout=60) as resp:  # nosec - arquivo público
            data = resp.read()
        # Validação completa
        try:
            text = data.decode('utf-8')
        except UnicodeDecodeError as e:
            raise ValueError(f'UTF-8 inválido: {e}') from e
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError as e:
            raise ValueError(f'JSON inválido: {e}') from e
        if not isinstance(parsed, dict) or 'AvailableTranslations' not in parsed:
            raise ValueError('Estrutura inesperada: chave "AvailableTranslations" ausente')
        tmp.write_text(text, encoding='utf-8')
        tmp.replace(TRANSL_FILE)
        AmadonLogging.info(
            main_window if main_window else None,
            _("translations.download.success").format(duration=round(time.time()-start,2), size=len(data))
        )
    except Exception as e:  # pragma: no cover
        try:
            ERR_FILE.write_text(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Erro no download: {e}\n", encoding='utf-8')
        except Exception:
            pass
        AmadonLogging.error(main_window if main_window else None, _("translations.download.error").format(error=e))


def run():
    """Ponto de entrada principal para iniciar a aplicação GUI."""
    logging.basicConfig(level=logging.INFO)
    # Remove arquivo existente (refresh forçado) ANTES de iniciar UI, conforme pedido
    try:
        if TRANSL_FILE.exists():
            TRANSL_FILE.unlink()
    except Exception:
        pass

    app = QApplication(sys.argv)
    # Aplica tema ANTES de criar a janela para evitar flash branco
    apply_global_theme(app)
    window = main()  # obtém / cria instância global de MainWindow já com stylesheet ativo

    # Exemplos iniciais (podem ser removidos posteriormente)
    MensagensStatus.curto(window, "Pronto")
    MensagensStatus.longo(window, "Sistema")

    MensagensStatus.principal(window, "Amadon iniciado")
    AmadonLogging.info(window, "Aplicação Amadon iniciada com sucesso")

    window.show()
    # Inicia download em background imediatamente após criação/mostra da janela
    threading.Thread(target=_background_download_translations, daemon=True).start()
    try:
        exit_code = app.exec()
        AmadonLogging.info(window, f"Aplicação encerrada normalmente com código: {exit_code}")
        # Salva settings (persistência)
        settings.save()
        sys.exit(exit_code)
    except Exception as e:  # pragma: no cover
        AmadonLogging.error_with_exception(window, "Erro durante execução da aplicação", e)
        try:
            settings.save()
        except Exception:
            pass
        sys.exit(1)


if __name__ == "__main__":  # pragma: no cover
    run()
