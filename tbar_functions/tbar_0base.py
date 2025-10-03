from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any
from i18n import _

def _safe_logger():
    import logging
    return logging.getLogger('Amadon')

class ToolBar_Base(ABC):
    """Base para ações da toolbar.

    Recebe a janela principal em context. Fornece helpers para logging e
    atualização de status, permitindo que cada classe concreta concentre a
    lógica de interface e mensagens.
    """
    def __init__(self, context: Any | None = None) -> None:
        self.context = context

    # ---- Helpers ----
    def _log_info(self, key: str):
        try:
            from mensagens import AmadonLogging
            if self.context is not None:
                AmadonLogging.info(self.context, _(key))
            else:
                _safe_logger().info(_(key))
        except Exception:
            _safe_logger().info(_(key))

    def _log_debug(self, key: str):
        try:
            from mensagens import AmadonLogging
            if self.context is not None:
                AmadonLogging.debug(self.context, _(key))
            else:
                _safe_logger().debug(_(key))
        except Exception:
            _safe_logger().debug(_(key))

    def _status_curto(self, key: str):
        if self.context is None:
            return
        try:
            from mensagens import MensagensStatus
            MensagensStatus.curto(self.context, _(key))
        except Exception:
            pass

    def _status_longo(self, key: str):
        if self.context is None:
            return
        try:
            from mensagens import MensagensStatus
            MensagensStatus.longo(self.context, _(key))
        except Exception:
            pass

    def _status_principal(self, key: str):
        if self.context is None:
            return
        try:
            from mensagens import MensagensStatus
            MensagensStatus.principal(self.context, _(key))
        except Exception:
            pass

    @abstractmethod
    def GenerateData(self) -> str:  # noqa: N802
        """Executa a ação e retorna representação textual (diagnóstico)."""
        raise NotImplementedError
