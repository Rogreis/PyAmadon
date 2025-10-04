import sys
import logging
from PySide6.QtWidgets import QApplication

from mensagens import AmadonLogging, MensagensStatus
from main_window import main, main_window
from app_settings import apply_global_theme, settings


def run():
    """Ponto de entrada principal para iniciar a aplicação GUI."""
    logging.basicConfig(level=logging.INFO)
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
