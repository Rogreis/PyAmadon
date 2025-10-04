"""Utilitário central para exibição de mensagens na barra de status.

Esta classe concentra a lógica de atualização dos três elementos de status:
- status_curto
- status_longo
- status_msg (label expansível com elipse)

Cada método é estático e recebe a janela principal (ou qualquer objeto que
exponha os atributos necessários). Isso facilita testes e reutilização.
"""
from typing import Any, Optional
import traceback

from PySide6.QtCore import QTimer


class MensagensStatus:
    """Métodos estáticos para manipular mensagens de status da aplicação."""

    @staticmethod
    def curto(win: Any, texto: Any) -> None:
        if hasattr(win, "status_curto"):
            win.status_curto.setText(str(texto))

    @staticmethod
    def longo(win: Any, texto: Any) -> None:
        if hasattr(win, "status_longo"):
            win.status_longo.setText(str(texto))

    @staticmethod
    def principal(win: Any, texto: Any) -> None:
        if hasattr(win, "status_msg"):
            # Assume ElidedLabel com setText já fazendo elipse
            win.status_msg.setText(str(texto))

    @staticmethod
    def ambos(win: Any, curto: Any, longo: Any, principal: Optional[Any] = None) -> None:
        MensagensStatus.curto(win, curto)
        MensagensStatus.longo(win, longo)
        if principal is not None:
            MensagensStatus.principal(win, principal)

    @staticmethod
    def temporario_principal(win: Any, texto: Any, ms: int = 3000) -> None:
        """Mostra uma mensagem principal temporária e restaura a anterior após 'ms' ms."""
        if not hasattr(win, "status_msg"):
            return
        anterior = getattr(win, "_status_msg_principal_backup", win.status_msg.fullText() if hasattr(win.status_msg, "fullText") else win.status_msg.text())
        MensagensStatus.principal(win, texto)
        win._status_msg_principal_backup = anterior
        QTimer.singleShot(ms, lambda: MensagensStatus.principal(win, anterior))

    @staticmethod
    def limpar_principal(win: Any) -> None:
        if hasattr(win, "status_msg"):
            win.status_msg.clear()


class AmadonLogging:
    """Utilitário estático para operações de logging desacopladas da janela.

    Fornece métodos de atalho que verificam a existência de 'logger' no objeto
    passado (tipicamente a MainWindow) antes de registrar a mensagem.
    """

    @staticmethod
    def debug(ctx: Any, msg: str):
        if hasattr(ctx, 'logger'):
            ctx.logger.debug(msg)

    @staticmethod
    def info(ctx: Any, msg: str):
        if hasattr(ctx, 'logger'):
            ctx.logger.info(msg)

    @staticmethod
    def warning(ctx: Any, msg: str):
        if hasattr(ctx, 'logger'):
            ctx.logger.warning(msg)

    @staticmethod
    def error(ctx: Any, msg: str):
        if hasattr(ctx, 'logger'):
            ctx.logger.error(msg)

    @staticmethod
    def fatal(ctx: Any, msg: str):
        if hasattr(ctx, 'logger') and hasattr(ctx.logger, 'fatal'):
            ctx.logger.fatal(msg)

    @staticmethod
    def trace(ctx: Any, msg: str):
        if hasattr(ctx, 'logger') and hasattr(ctx.logger, 'trace'):
            ctx.logger.trace(msg)

    @staticmethod
    def exception(ctx: Any, msg: str):
        if hasattr(ctx, 'logger'):
            ctx.logger.exception(msg)

    @staticmethod
    def error_with_exception(ctx: Any, msg: str, exc: BaseException, include_traceback: bool = True):
        """Registra um erro detalhado a partir de uma exception explicitamente fornecida.

        Diferente de `exception()`, que depende do contexto atual (dentro de um bloco except),
        este método recebe o objeto da exception e monta manualmente a mensagem completa.

        Parâmetros:
        - ctx: normalmente a janela principal ou qualquer objeto com atributo `logger`.
        - msg: mensagem de contexto descritiva do que estava sendo feito.
        - exc: a instância de exception capturada.
        - include_traceback: se True, inclui o traceback formatado.
        """
        if not hasattr(ctx, 'logger'):
            return

        exc_type = type(exc).__name__
        exc_msg = str(exc)
        exc_repr = repr(exc)

        base = f"{msg} | Exception: {exc_type}: {exc_msg} | Repr: {exc_repr}"
        if include_traceback and getattr(exc, '__traceback__', None) is not None:
            tb_txt = ''.join(traceback.format_exception(exc.__class__, exc, exc.__traceback__))
            base = f"{base}\nTraceback:\n{tb_txt}".rstrip()

        ctx.logger.error(base)
