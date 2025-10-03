from __future__ import annotations
from .tbar_0base import ToolBar_Base
from i18n import _

class ToolBar_Assuntos(ToolBar_Base):
    def GenerateData(self) -> str:  # noqa: N802
        self._log_info("log.open.assuntos")
        self._status_curto("status.curto.ass")
        self._status_principal("status.msg.assuntos")
        return _("status.msg.assuntos")