from __future__ import annotations
from .tbar_0base import ToolBar_Base
from i18n import _

class ToolBar_Busca(ToolBar_Base):
    def GenerateData(self) -> str:  # noqa: N802
        self._log_info("log.open.busca")
        self._status_curto("status.curto.bus")
        self._status_principal("status.msg.busca")
        return _("status.msg.busca")