from __future__ import annotations
from .tbar_0base import ToolBar_Base
from i18n import _

class ToolBar_Configuracao(ToolBar_Base):
    def GenerateData(self) -> str:  # noqa: N802
        self._log_info("log.open.configuracao")
        self._status_curto("status.curto.cfg")
        self._status_principal("status.msg.configuracao")
        return _("status.msg.configuracao")