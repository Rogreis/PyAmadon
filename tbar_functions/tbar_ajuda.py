from __future__ import annotations
from .tbar_0base import ToolBar_Base
from i18n import _

class ToolBar_Ajuda(ToolBar_Base):
    def GenerateData(self) -> str:  # noqa: N802
        self._log_info("log.open.ajuda")
        self._status_curto("status.curto.help")
        self._status_principal("status.msg.ajuda")
        return _("status.msg.ajuda")